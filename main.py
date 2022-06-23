#Setup

import sys
import requests
import tabulate
from IPython.display import HTML, display

impc_api_url = "https://www.gentar.org/impc-dev-api/"
impc_api_search_url = f"{impc_api_url}/genes"
impc_api_gene_bundle_url = f"{impc_api_url}/geneBundles"

# 1-Given a gene id, retrieve all the phenotypes related to it (id and name)

mgi_accession_id = str(sys.argv[1])

gene_url = f"{impc_api_search_url}/{mgi_accession_id}"
gene_data = requests.get(gene_url).json()

p_list = gene_data['significantMpTermNames']
display(HTML(tabulate.tabulate([i for i in p_list], headers="Phenotype Name", tablefmt='html')))

# 11- Which parameters have been measured for a particular knockout EASY

knockout = "MGI:104636"
gene_info = requests.get(impc_api_search_url+"/"+knockout).json()

if gene_info['phenotypingDataAvailable']:
    geneBundle = requests.get(gene_info['_links']['geneBundle']['href']).json()
    gen_imgs = geneBundle['geneImages']
    par_list=[]
    l={}
    for i in gen_imgs:
        l={"Parameter Name":i['parameterName']}
        if l not in par_list:
            par_list.append(l)
    display(HTML(tabulate.tabulate([i.values() for i in par_list], headers=par_list[0].keys(), tablefmt='html')))

else:
    print("No parameters available for this knockout gene.")


# 12- Which parameters identified a significant finding for a particular knockout line (colony) EASY

knockout = "MGI:104636"
gene_info = requests.get(impc_api_search_url+"/"+knockout).json()

if gene_info['phenotypingDataAvailable']:
    geneBundle = requests.get(gene_info['_links']['geneBundle']['href']).json()
    gen_stat = geneBundle['geneStatisticalResults']
    par_list=[]
    l={}
    for i in gen_stat:
        if i['pvalue'] == None or i['pvalue'] > 0.05:
            continue
        else:
            l={"Parameter Name":i['parameterName'], "pvalue":i['pvalue']}
            par_list.append(l)
    if len(par_list) == 0:
        print("No statistically relevant parameters found for this knockout gene")
    else:
        display(HTML(tabulate.tabulate([i.values() for i in par_list], headers=par_list[0].keys(), tablefmt='html')))

else:
    print("No statistically significant parameters available for this knockout gene.")

# 16- Full table of genes and all identified phenotypes EASY

gene_list = requests.get(impc_api_search_url+'?page=0&size=1000').json()
pages = gene_list['page']['totalPages']
max_elem = gene_list['page']['totalElements']
d = {}
list_d = []
for i in range(0,pages):
    gl = requests.get(impc_api_search_url+'?page='+str(i)+'&size='+str(max_elem)).json()
    for g in gl['_embedded']['genes']:
        d = {"Gene": g['mgiAccessionId'], "Identified phenotypes": g['significantMpTermIds']}
        list_d.append(d)

display(HTML(tabulate.tabulate([i.values() for i in list_d], headers=list_d[0].keys(), tablefmt='html')))