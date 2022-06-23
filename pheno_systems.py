import sys
import requests
import pandas as pd
import urllib.request as url

impc_api_url = "https://www.gentar.org/impc-dev-api/"
impc_api_search_url = f"{impc_api_url}/genes"


def main():
    systems = ["immune system phenotype", "integument phenotype", "adipose tissue phenotype",
               "hearing/vestibular/ear phenotype", "hematopoietic system phenotype", "craniofacial phenotype",
               "cardiovascular system phenotype", "renal/urinary system phenotype", "homeostasis/metabolism phenotype",
               "pigmentation phenotype", "limbs/digits/tail phenotype", "nervous system phenotype",
               "vision/eye phenotype", "liver/biliary system phenotype", "respiratory system phenotype",
               "behavior/neurological phenotype", "skeleton phenotype", "mortality/aging",
               "reproductive system phenotype", "endocrine/exocrine gland phenotype",
               "growth/size/body region phenotype", "embryo phenotype", "muscle phenotype",
               "digestive/alimentary phenotype"]

    if str(sys.argv[1]) == '1':
        pheno_list(systems)
    else:
        full_gene_table(systems)


def pheno_list(systems):
    # Taking as input a txt file with gene symbol/mgi id, retrieve the list of pheno.
    inp = str(sys.argv[2])

    s = str(sys.argv[3])
    if s == "t":
        sep = "\t"
    elif s == "s":
        sep = " "
    elif s in ",;.":
        sep = s
    else:
        sys.exit("Separator not valid, please change it.")
    genes = pd.read_csv(inp, sep=sep, header=None)

    if genes.shape[0] > 1 & genes.shape[1] == 1:
        genes = genes.swapaxes(axis1=1, axis2=0)
    genes = genes.values.tolist()[0]

    # if there are symbols in the input, map them into MGI ids

    final_list = []
    sym_list = []
    for i in genes:
        if 'MGI:' in i:
            final_list.append(i)
        else:
            sym_list.append(i)

    if len(sym_list) != 0:
        sym_list = ",".join(sym_list)
        biodbnet = f'https://biodbnet.abcc.ncifcrf.gov/webServices/rest.php/biodbnetRestApi.xml?method=db2db&format=row&input=genesymbol&inputValues={sym_list}&outputs=mgiid&taxonId=10090'
        u = url.urlopen(biodbnet)
        db = pd.read_xml(u, elems_only=True)
        sym_list = []
        for i in range(0, len(db)):
            x = db['MGIID'][i][4:]
            if x != '':
                sym_list.append(x)
        if len(sym_list) == 0 and len(final_list) == 0:
            sys.exit("It was not possible to map the input.")
        else:
            final_list.extend(sym_list)

    df = pd.DataFrame(data='', index=final_list, columns=systems)

    for i in df.index:
        gene_url = f"{impc_api_search_url}/{i}"
        gene_data = requests.get(gene_url).json()
        sigMp = gene_data['significantMpTerms']
        if sigMp is None:
            continue
        l = []
        for j in sigMp:
            if j['mpTermId'] is None:
                continue
            l.append(j['mpTermId'])
            for k in j['topLevelAncestors']:
                if df.loc[i, k['mpTermName']] == '':
                    df.loc[i, k['mpTermName']] = l
                else:
                    df.loc[i, k['mpTermName']].extend(l)
            l=[]


    df.to_csv(sys.argv[4], sep="\t", header=True, index=True)


def full_gene_table(systems):

    gene_list = requests.get(impc_api_search_url + '?page=0&size=1000').json()
    pages = gene_list['page']['totalPages']
    genes_info = gene_list['_embedded']['genes']

    for pn in range(1, pages):
        gp = requests.get(impc_api_search_url + f'?page={pn}&size=1000').json()['_embedded']['genes']
        genes_info += gp

    ids = []
    gp = genes_info.copy()
    for i in genes_info:
        if i['significantMpTerms'] is None:
            gp.remove(i)
        else:
            ids.append(i['mgiAccessionId'])
    del(genes_info)

    df = pd.DataFrame(data='', index=ids, columns=systems)
    for i in gp:
        g = i['mgiAccessionId']
        sigMp = i['significantMpTerms']
        if sigMp is None:
            continue
        l = []
        for j in sigMp:
            if j['mpTermId'] is None:
                continue
            l.append(j['mpTermId'])
            for k in j['topLevelAncestors']:
                if df.loc[g, k['mpTermName']] == '':
                    df.loc[g, k['mpTermName']] = l
                else:
                    df.loc[g, k['mpTermName']].extend(l)
            l = []

    df.to_csv(sys.argv[2], sep="\t", header=True, index=True)

if __name__ == "__main__":
    main()