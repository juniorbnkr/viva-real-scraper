from browser import Browser

browser = Browser()
url='https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/agua-branca/apartamento_residencial/#preco-ate=4000&preco-total=sim'

# file = browser.list_all_to_csv(url)
# print(file)
browser.extract_infos('imoveis-223-12192022_11:11:02.csv')