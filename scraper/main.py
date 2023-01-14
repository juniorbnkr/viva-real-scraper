from browser import Browser
import os,glob

urls={
    'lapa':"https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/lapa/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim",
    'pinheiros':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/pinheiros/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'stacecilia':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/centro/santa-cecilia/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'aguabranca':"https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/agua-branca/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim",
    'vlromana':"https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/vila-romana/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim",
    'vlleopoldina':"https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/vila-leopoldina/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim",
    'pompeia':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/pompeia/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'altolapa':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/alto-da-lapa/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'sumare':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/sumare/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'barra funda':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/barra-funda/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'vlanastacio':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/vila-anastacio/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'belavista':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/centro/bela-vista/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'consolacao':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/centro/consolacao/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    'liberdade':'https://www.vivareal.com.br/aluguel/sp/sao-paulo/centro/liberdade/apartamento_residencial/#area-desde=30&preco-ate=3800&preco-total=sim',
    
}

browser = Browser()

extension = 'csv'
csv_files = glob.glob('*.{}'.format(extension))

if not csv_files:    
    for i,url in urls.items():
        file = browser.list_all_to_csv(url,i)
        csv_files.append(file)

for file in csv_files:
    browser.extract_infos(file)

browser.quit()

# browser.fix_infos("lat")