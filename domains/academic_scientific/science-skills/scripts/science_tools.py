#!/usr/bin/env python3
"""
Google DeepMind Science-Skills Engine
=====================================
Unified scientific computing & discovery toolkit for computational biology, structural bioinformatics,
and chemical property informatics.

Integrates:
- UniProt Knowledgebase (Sequence, Gene, Annotation, Topology)
- AlphaFold DB (Predicted 3D structures, per-residue pLDDT confidence, PAE)
- RCSB Protein Data Bank (Experimental structures, X-ray/Cryo-EM resolution)
- PubChem PUG-REST (Molecular formula, SMILES, Lipinski Rule-of-5, physicochemical metrics)
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

import time

USER_AGENT = "DeepMind-ScienceSkills-Agent/1.0 (Computational Biology & Chemistry Toolkit)"

def _fetch_json(url, timeout=15, max_retries=3):
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            return {"error": f"HTTP Error {e.code}: {e.reason}", "url": url}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return {"error": str(e), "url": url}
    return {"error": "Max retries reached", "url": url}

def _download_file(url, target_path, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response, open(target_path, "wb") as out_f:
            out_f.write(response.read())
        return True, target_path
    except Exception as e:
        return False, str(e)

# ------------------------------------------------------------------------------
# 1. UniProt Knowledgebase
# ------------------------------------------------------------------------------
def fetch_uniprot(accession_or_query):
    query = accession_or_query.strip()
    is_accession = len(query) in [6, 10] and (query[0].isalpha() or query[0].isdigit()) and not " " in query
    
    if is_accession:
        url = f"https://rest.uniprot.org/uniprotkb/{query}.json"
        data = _fetch_json(url)
        if "error" not in data:
            return parse_uniprot_entry(data)
    
    # Fallback to search
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://rest.uniprot.org/uniprotkb/search?query={encoded_query}&size=3&format=json"
    search_data = _fetch_json(search_url)
    results = search_data.get("results", [])
    if not results:
        return {"status": "not_found", "query": query, "message": "No matching UniProt entry found"}
    return parse_uniprot_entry(results[0])

def parse_uniprot_entry(entry):
    acc = entry.get("primaryAccession", "N/A")
    id_name = entry.get("uniProtkbId", "N/A")
    organism = entry.get("organism", {}).get("scientificName", "N/A")
    taxon_id = entry.get("organism", {}).get("taxonId", "N/A")
    
    genes = entry.get("genes", [])
    gene_name = genes[0].get("geneName", {}).get("value", "N/A") if genes else "N/A"
    
    protein_desc = entry.get("proteinDescription", {})
    rec_name = protein_desc.get("recommendedName", {}).get("fullName", {}).get("value", "N/A")
    
    seq_info = entry.get("sequence", {})
    seq = seq_info.get("value", "")
    length = seq_info.get("length", len(seq))
    mol_weight = seq_info.get("molWeight", "N/A")
    
    functions = []
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            for text in comment.get("texts", []):
                functions.append(text.get("value", ""))
    
    return {
        "status": "success",
        "database": "UniProtKB",
        "accession": acc,
        "entry_name": id_name,
        "recommended_name": rec_name,
        "gene": gene_name,
        "organism": f"{organism} (TaxID: {taxon_id})",
        "length": length,
        "molecular_weight_da": mol_weight,
        "function_summary": " ".join(functions)[:600] + ("..." if len(" ".join(functions)) > 600 else ""),
        "sequence_preview": seq[:60] + "..." if len(seq) > 60 else seq,
        "full_sequence_length": len(seq),
        "uniprot_url": f"https://www.uniprot.org/uniprotkb/{acc}"
    }

# ------------------------------------------------------------------------------
# 2. AlphaFold Structure Database
# ------------------------------------------------------------------------------
def fetch_alphafold(accession, download_dir=None):
    acc = accession.strip().upper()
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"
    data = _fetch_json(url)
    
    if isinstance(data, dict) and "error" in data:
        return {"status": "error", "accession": acc, "message": data["error"]}
    if not isinstance(data, list) or len(data) == 0:
        return {"status": "not_found", "accession": acc, "message": "No AlphaFold prediction found for this accession"}
    
    pred = data[0]
    entry_id = pred.get("entryId", acc)
    uniprot_id = pred.get("uniprotAccession", acc)
    global_plddt = pred.get("globalPlddt", "N/A")
    pdb_url = pred.get("pdbUrl")
    cif_url = pred.get("cifUrl")
    pae_image_url = pred.get("paeImageUrl")
    
    res = {
        "status": "success",
        "database": "AlphaFold DB",
        "entry_id": entry_id,
        "uniprot_accession": uniprot_id,
        "global_plddt": global_plddt,
        "confidence_assessment": (
            "Very High (pLDDT > 90)" if isinstance(global_plddt, (int, float)) and global_plddt >= 90
            else "Confident (70 <= pLDDT < 90)" if isinstance(global_plddt, (int, float)) and global_plddt >= 70
            else "Low (50 <= pLDDT < 70)" if isinstance(global_plddt, (int, float)) and global_plddt >= 50
            else "Very Low / Disordered (pLDDT < 50)" if isinstance(global_plddt, (int, float))
            else "N/A"
        ),
        "pdb_url": pdb_url,
        "cif_url": cif_url,
        "pae_image_url": pae_image_url,
        "alphafold_page": f"https://alphafold.ebi.ac.uk/entry/{uniprot_id}"
    }
    
    if download_dir and pdb_url:
        os.makedirs(download_dir, exist_ok=True)
        local_pdb = os.path.join(download_dir, f"AF-{uniprot_id}-F1-model_v4.pdb")
        success, info = _download_file(pdb_url, local_pdb)
        if success:
            res["local_pdb_path"] = local_pdb
        else:
            res["download_error"] = info
            
    return res

# ------------------------------------------------------------------------------
# 3. RCSB Protein Data Bank (PDB)
# ------------------------------------------------------------------------------
def fetch_pdb(pdb_id, download_dir=None):
    pdb = pdb_id.strip().upper()
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb}"
    data = _fetch_json(url)
    
    if "error" in data:
        return {"status": "error", "pdb_id": pdb, "message": data["error"]}
    
    struct_title = data.get("struct", {}).get("title", "N/A")
    exptl = data.get("exptl", [{}])[0]
    method = exptl.get("method", "N/A")
    
    resolution = "N/A"
    if "rcsb_entry_info" in data:
        resolution = data["rcsb_entry_info"].get("resolution_combined", ["N/A"])[0]
    
    primary_citation = data.get("rcsb_primary_citation", {})
    citation_title = primary_citation.get("title", "N/A")
    doi = primary_citation.get("doi", "N/A")
    
    res = {
        "status": "success",
        "database": "RCSB Protein Data Bank",
        "pdb_id": pdb,
        "title": struct_title,
        "experimental_method": method,
        "resolution_angstrom": resolution,
        "primary_citation": citation_title,
        "doi": doi,
        "rcsb_url": f"https://www.rcsb.org/structure/{pdb}",
        "pdb_download_url": f"https://files.rcsb.org/download/{pdb}.pdb"
    }
    
    if download_dir:
        os.makedirs(download_dir, exist_ok=True)
        local_pdb = os.path.join(download_dir, f"{pdb}.pdb")
        success, info = _download_file(f"https://files.rcsb.org/download/{pdb}.pdb", local_pdb)
        if success:
            res["local_pdb_path"] = local_pdb
        else:
            res["download_error"] = info
            
    return res

# ------------------------------------------------------------------------------
# 4. Chemical & Pharmacology (PubChem + EMBL ChEMBL + NCI Fallback)
# ------------------------------------------------------------------------------
def fetch_molecule(compound_name_or_cid):
    query = compound_name_or_cid.strip()
    is_cid = query.isdigit()
    
    properties = "MolecularFormula,MolecularWeight,CanonicalSMILES,InChIKey,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,RotatableBondCount"
    if is_cid:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{query}/property/{properties}/JSON"
    else:
        encoded = urllib.parse.quote(query)
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/property/{properties}/JSON"
        
    data = _fetch_json(url)
    if "error" not in data and data.get("PropertyTable", {}).get("Properties"):
        p = data["PropertyTable"]["Properties"][0]
        cid = p.get("CID")
        mw = float(p.get("MolecularWeight", 0))
        logp = float(p.get("XLogP", 0)) if p.get("XLogP") is not None else None
        hbd = int(p.get("HBondDonorCount", 0))
        hba = int(p.get("HBondAcceptorCount", 0))
        tpsa = float(p.get("TPSA", 0)) if p.get("TPSA") is not None else None
        
        lipinski_violations = 0
        if mw > 500: lipinski_violations += 1
        if logp is not None and logp > 5: lipinski_violations += 1
        if hbd > 5: lipinski_violations += 1
        if hba > 10: lipinski_violations += 1
        
        return {
            "status": "success",
            "database": "PubChem PUG-REST",
            "compound_query": query,
            "cid": cid,
            "molecular_formula": p.get("MolecularFormula"),
            "molecular_weight": mw,
            "canonical_smiles": p.get("CanonicalSMILES"),
            "inchikey": p.get("InChIKey"),
            "xlogp": logp,
            "tpsa_angstrom2": tpsa,
            "h_bond_donors": hbd,
            "h_bond_acceptors": hba,
            "rotatable_bonds": p.get("RotatableBondCount"),
            "lipinski_rule_of_five": {
                "violations_count": lipinski_violations,
                "drug_likeness": "Pass (Likely Drug-like)" if lipinski_violations <= 1 else "Fail / Poor Bioavailability",
                "criteria": {
                    "mw_le_500": mw <= 500,
                    "logp_le_5": (logp is not None and logp <= 5),
                    "hbd_le_5": hbd <= 5,
                    "hba_le_10": hba <= 10
                }
            },
            "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
        }
    
    # Fallback to EMBL-EBI ChEMBL API
    chembl_url = f"https://www.ebi.ac.uk/chembl/api/data/molecule.json?pref_name__iexact={urllib.parse.quote(query)}"
    chembl_data = _fetch_json(chembl_url)
    if "error" not in chembl_data and chembl_data.get("molecules"):
        mol = chembl_data["molecules"][0]
        chembl_id = mol.get("molecule_chembl_id")
        props = mol.get("molecule_properties") or {}
        structs = mol.get("molecule_structures") or {}
        
        mw = float(props.get("full_mwt", 0)) if props.get("full_mwt") else 0.0
        logp = float(props.get("alogp", 0)) if props.get("alogp") else None
        hbd = int(props.get("hbd", 0)) if props.get("hbd") is not None else 0
        hba = int(props.get("hba", 0)) if props.get("hba") is not None else 0
        tpsa = float(props.get("psa", 0)) if props.get("psa") else None
        ro5 = int(props.get("num_ro5_violations", 0)) if props.get("num_ro5_violations") is not None else 0
        
        return {
            "status": "success",
            "database": "EMBL-EBI ChEMBL (Fallback)",
            "compound_query": query,
            "chembl_id": chembl_id,
            "preferred_name": mol.get("pref_name", query),
            "molecular_formula": props.get("full_molformula"),
            "molecular_weight": mw,
            "canonical_smiles": structs.get("canonical_smiles"),
            "standard_inchi_key": structs.get("standard_inchi_key"),
            "alogp": logp,
            "tpsa_angstrom2": tpsa,
            "h_bond_donors": hbd,
            "h_bond_acceptors": hba,
            "rotatable_bonds": props.get("rtb"),
            "lipinski_rule_of_five": {
                "violations_count": ro5,
                "drug_likeness": "Pass (Likely Drug-like)" if ro5 <= 1 else "Fail / Poor Bioavailability"
            },
            "chembl_url": f"https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id}/"
        }
    
    # Second Fallback to NCI CACTUS Resolver
    try:
        smiles_req = urllib.request.Request(f"https://cactus.nci.nih.gov/chemical/structure/{urllib.parse.quote(query)}/smiles")
        with urllib.request.urlopen(smiles_req, timeout=10) as r:
            smiles = r.read().decode("utf-8").strip()
        mw_req = urllib.request.Request(f"https://cactus.nci.nih.gov/chemical/structure/{urllib.parse.quote(query)}/mw")
        with urllib.request.urlopen(mw_req, timeout=10) as r:
            mw = float(r.read().decode("utf-8").strip())
        formula_req = urllib.request.Request(f"https://cactus.nci.nih.gov/chemical/structure/{urllib.parse.quote(query)}/formula")
        with urllib.request.urlopen(formula_req, timeout=10) as r:
            formula = r.read().decode("utf-8").strip()
            
        return {
            "status": "success",
            "database": "NCI CACTUS CIR (Fallback)",
            "compound_query": query,
            "molecular_formula": formula,
            "molecular_weight": mw,
            "canonical_smiles": smiles
        }
    except Exception as e:
        return {"status": "error", "query": query, "message": f"Molecule not resolved: {str(e)}"}

# ------------------------------------------------------------------------------
# CLI Main Entrypoint
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Google DeepMind Science-Skills: Structural Biology & Chemical Informatics Engine"
    )
    parser.add_argument("--mode", "-m", choices=["uniprot", "alphafold", "pdb", "molecule", "auto"], default="auto",
                        help="Operation mode: uniprot | alphafold | pdb | molecule | auto")
    parser.add_argument("--query", "-q", required=True, help="Accession, PDB ID, compound name or keyword")
    parser.add_argument("--download-dir", "-d", default=None, help="Directory to download PDB/structure files")
    parser.add_argument("--output", "-o", default=None, help="File path to save JSON output")
    
    args = parser.parse_args()
    q = args.query.strip()
    mode = args.mode
    
    # Auto-detection heuristic
    if mode == "auto":
        if len(q) == 4 and (q[0].isdigit() or q[-1].isdigit()):
            mode = "pdb"
        elif len(q) in [6, 10] and q[0].isalpha() and (q[1].isdigit() or q.isalnum()):
            mode = "alphafold"
        elif any(char in q for char in ["-", "_", " "]) or not (len(q) in [4, 6, 10] and q.isalnum()):
            mode = "molecule"
        else:
            mode = "uniprot"

    results = {}
    print(f"🔬 [Science-Skills] Running in mode: {mode.upper()} for query: '{q}'...")
    
    try:
        if mode == "uniprot":
            results = fetch_uniprot(q)
        elif mode == "alphafold":
            results = fetch_alphafold(q, download_dir=args.download_dir)
            # If successful, also enrich with UniProt info
            if results.get("status") == "success":
                up_info = fetch_uniprot(q)
                if up_info.get("status") == "success":
                    results["protein_metadata"] = up_info
        elif mode == "pdb":
            results = fetch_pdb(q, download_dir=args.download_dir)
        elif mode == "molecule":
            results = fetch_molecule(q)
        else:
            results = {"status": "error", "message": f"Unsupported mode: {mode}"}
            
    except Exception as e:
        results = {"status": "exception", "error": str(e)}

    # Render formatted output
    formatted_json = json.dumps(results, indent=2, ensure_ascii=False)
    print("\n" + "=" * 60)
    print(f"📊 Science-Skills Result ({results.get('database', mode)}):")
    print("=" * 60)
    print(formatted_json)
    print("=" * 60)
    
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(formatted_json)
        print(f"\n💾 Results exported to: {args.output}")

if __name__ == "__main__":
    main()
