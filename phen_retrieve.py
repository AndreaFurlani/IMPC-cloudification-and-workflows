import sys
import requests
import pandas as pd
import urllib.request as url

impc_api_url = "https://www.gentar.org/impc-dev-api/"
impc_api_search_url = f"{impc_api_url}/genes"
impc_api_gene_bundle_url = f"{impc_api_url}/geneBundles"

def main():

    if str(sys.argv[1]) == '1':
        pheno_list()
    else:
        full_gene_table()


def pheno_list():

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

    df = pd.DataFrame()
    g = []
    p = []
    ignored_ids = []

    for i in final_list:

        t = []
        gene_url = f"{impc_api_search_url}/{i}"
        try:
            gene_data = requests.get(gene_url).json()
        except:
            ignored_ids.append(i)
            continue
        g.append(gene_data['mgiAccessionId'])
        if gene_data['significantMpTerms'] is not None:
            for j in gene_data['significantMpTerms']:
                t.append(j['mpTermId'])
        else:
            t.append("None")
        p.append(t)
        del (t, gene_url, gene_data)

    df['MGI id'] = g
    df['MP term list'] = p

    for i in range(0, len(df)):
        df['MP term list'][i] = str(df['MP term list'][i])[1:-1].replace("'", "")
        df['MP term list'][i] = str(df['MP term list'][i]).replace(" ", "")
    df.to_csv(sys.argv[4], header=True, index=False, sep="\t", index_label=False)
    pd.DataFrame(ignored_ids,columns=['ignored ids']).to_csv(sys.argv[5], header=True, index=False, sep="\t", index_label=False)

def full_gene_table():

    gene_list = requests.get(impc_api_search_url + '?page=0&size=1000').json()
    pages = gene_list['page']['totalPages']
    max_elem = gene_list['page']['totalElements']
    d = {}
    list_d = []
    for i in range(0, pages):
        gl = requests.get(impc_api_search_url + '?page=' + str(i) + '&size=' + str(max_elem)).json()
        for g in gl['_embedded']['genes']:
            if g['significantMpTerms'] is None:
                d = {"Gene": g['mgiAccessionId'], "Identified phenotypes": "None"}
            else:
                d = {"Gene": g['mgiAccessionId'], "Identified phenotypes": [ sub['mpTermId'] for sub in g['significantMpTerms'] ]}
            list_d.append(d)

    df = pd.DataFrame()
    g = []
    p = []
    for i in list_d:
        g.append(i['Gene'])
        p.append(i['Identified phenotypes'])


    df['MGI id'] = g
    df['MP term list'] = p

    for i in range(0,len(df)):
        if df['MP term list'][i] != "None":
            df['MP term list'][i] = str(df['MP term list'][i])[1:-1].replace("'", "")

    empty = df[df['MP term list'] == "None"]
    df = df[df['MP term list'] != "None"]
    df.reset_index(drop=True, inplace=True)
    df.to_csv(sys.argv[2], header=True, index=False, sep="\t", index_label=False)
    empty.to_csv(sys.argv[3], header=True, index=False, sep="\t", index_label=False)

if __name__ == "__main__":
    main()