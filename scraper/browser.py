from selenium import webdriver
import time,datetime,os,sys,logging,csv
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
from sqlalchemy import create_engine  
from bs4 import BeautifulSoup 
import json 

import utils

logger = logging.getLogger("_")
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(utils.CustomFormatter())
logger.addHandler(ch)


if os.uname()[1] in ("cktta","JEITTO0012L","luiz.vieira"):
    local_test = True
else:    
    local_test = False
    
class Browser:
   
    def __init__(self):
        self = self
        options = Options()
        self.db_user=os.environ.get('vivadb_user')
        self.db_server=os.environ.get('vivadb_server')
        self.db_pass=os.environ.get('vivadb_pass')
        if not local_test:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--enable-automation")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-browser-side-navigation")
            options.add_argument("--disable-gpu")            
            options.add_argument("--disable-infobars")
            options.add_argument("--window-size=1920,1080")
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-setuid-sandbox")
            options.add_argument("--disable-extensions")
            mobile_emulation = {
			"deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
		    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" 
                }
            # options.add_experimental_option("mobileEmulation", mobile_emulation)
            self.driver = webdriver.Chrome(options=options)
            # self.driver = webdriver.Remote('http://selenium:4444/wd/hub',options=options,
                                        #    desired_capabilities=DesiredCapabilities.CHROME)
        else:
            user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
            profile = webdriver.FirefoxProfile() 
            profile.set_preference("general.useragent.override", user_agent)
            options.headless = False
            self.driver = webdriver.Firefox(profile,options=options,executable_path="/geckodriver")
            # self.driver.set_window_size(360,640)

    def list_all_to_csv(self,url,bairro):
        try:
            self.driver.get(url)
            self.driver.get_screenshot_as_file("screenshot.png")
            logger.info(" INICIALIZADO ")
            time.sleep(8)
            total_imoveis = int(self.driver.find_element(By.CLASS_NAME,"js-total-records").text.replace(".",""))
            logger.info(f"Listando {total_imoveis} imoveis... [{total_imoveis/35} paginacoes esperadas]")
            filename = f'{bairro}-{total_imoveis}-{datetime.datetime.now().strftime("%m%d%Y_%H:%M:%S")}.csv' 

            file = open(filename, 'w')

            try:
                self.driver.find_element(By.CLASS_NAME,"cookie-notifier__cta").click()
            except:
                pass

            lista = self.driver.find_element(By.CLASS_NAME,"results-list") 
            for imovel in self.driver.find_elements(By.CSS_SELECTOR,"[data-type='property']"):
                id = imovel.find_element(By.TAG_NAME,"div").get_attribute("id")
                link = imovel.find_element(By.CLASS_NAME,"js-card-title").get_attribute("href")
                with open(filename, 'a') as file:
                    writer = csv.writer(file)
                    writer.writerow([id,link])

            while self.driver.find_elements(By.CLASS_NAME,"js-change-page")[-1].get_attribute("data-disabled") == None:
                time.sleep(3)
                self.driver.find_elements(By.CLASS_NAME,"js-change-page")[-1].click()
                time.sleep(5)

                for imovel in self.driver.find_elements(By.CSS_SELECTOR,"[data-type='property']"):
                    id = imovel.find_element(By.TAG_NAME,"div").get_attribute("id")
                    link = imovel.find_element(By.CLASS_NAME,"js-card-title").get_attribute("href")
                    with open(filename, 'a') as file:
                        writer = csv.writer(file)
                        writer.writerow([id,link])
                        
            rowcount  = 0
            for row in open(filename):
                rowcount+= 1
            logger.info(f" listagem finalizada. {rowcount} imoveis registrados no arquivo {filename}")
            time.sleep(1)
            return filename       

        except Exception as e:
            logger.error(e)
            return False

    def extract_infos(self,filename):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_server}/viva_real?password={self.db_pass}', pool_recycle=3600)
        dbConnection    = sqlEngine.connect()
        df = pd.read_sql("SELECT * FROM viva_real.imoveis where monitorar = 0",dbConnection)

        df_csv = pd.read_csv(filename,header=None)
        df_csv = df_csv.drop_duplicates()
        logger.info(filename)
        for index, row in df_csv.iterrows():
            if row[0] in df['id'].values or not row[0] > 0:
                continue

            self.driver.get(row[1])
            time.sleep(4)
            
            try:
                self.driver.find_element(By.CLASS_NAME,"js-external-id").text
            except:
                logger.warning(f"inactive - {row[0]}")
                continue
            
            infos_text=''
            while infos_text == '':
                scripts=self.driver.find_elements(By.TAG_NAME,'script')
                for i in scripts:
                    try:
                        if 'lat:' in i.get_attribute("innerHTML"):
                            infos_text = i.get_attribute("innerHTML")
                    except:
                        time.sleep(1)
                        pass
            try:
                lat=infos_text.split("lat: ")[1].split("lon: ")[0].replace(",\n","").replace(" ","").replace("'","")
                lon=infos_text.split("lon: ")[1].split("},")[0].replace(",\n","").replace(" ","").replace("'","")
            except:
                lat=0
                lon=0
            try:
                zipcode = int(infos_text.split('zipCode":"')[1].split('","geoJson')[0])
            except:
                zipcode = -1
            
            try:
                self.driver.find_element(By.CLASS_NAME,"cookie-notifier__cta").click()
            except:
                pass

            try:
                title_condominium = self.driver.find_element(By.CLASS_NAME,'title__condominium').text
            except:
                title_condominium = ''

            html = self.driver.page_source
            #BeautifulSoup Convert page source code 
            bs=BeautifulSoup(html,'lxml')
            infos1=json.loads(bs.find_all("script",{"type":"application/ld+json"})[0].get_text())
            infos3=json.loads(bs.find_all("script",{"type":"application/ld+json"})[1].get_text())
            # lat=infos2.split("Ranking Manager data")[0]
            
            zona = infos1['itemListElement'][4]['item']['name'][0:14]
            bairro = infos1['itemListElement'][5]['item']['name']
            try:
                endereco = infos1['itemListElement'][6]['item']['name']
            except:
                endereco = self.driver.find_element(By.CLASS_NAME,'js-address').text
                
            try:
                numero = int(self.driver.find_element(By.CLASS_NAME,'js-address').text.split(', ')[1].split(" -")[0])
            except:
                numero = 0
            
            area = self.driver.find_element(By.CLASS_NAME,'js-area').text
            quartos = utils.check_int(self.driver.find_element(By.CLASS_NAME,'js-bedrooms').text.split(' ')[0])            
            vagas = utils.check_int(self.driver.find_element(By.CLASS_NAME,'js-parking').text.split(' ')[0])
            anunciante = self.driver.find_element(By.CLASS_NAME,'publisher__name').text
            if len(anunciante)>35:anunciante=anunciante[:35]

            time. sleep(2)
            try:
                self.driver.find_element(By.CLASS_NAME,'js-amenities-button').click()
                time.sleep(1)
                caracteristicas = self.driver.find_element(By.CLASS_NAME,"amenities__list").text
                caracteristicas = caracteristicas.replace("\n",',')
                self.driver.find_element(By.CLASS_NAME,'js-close').click()

            except:
                caracteristicas = ''

            try:
                self.driver.find_element(By.CLASS_NAME,'js-see-phone').click()
                time.sleep(1)
                telefone = self.driver.find_element(By.CLASS_NAME,"post-lead-success__link").text
                self.driver.find_elements(By.CLASS_NAME,'js-close')[1].click()

            except:
                telefone = ''
                                   
            data = {
                'id':row[0],
                'url':row[1],
                'external_id':self.driver.find_element(By.CLASS_NAME,'js-external-id').text,
                'title__condominium':title_condominium,
                'endereco':endereco,   
                'numero':numero,
                'bairro':bairro,
                'zona':zona,
                'cep':0,
                'distrito':0,
                'monitorar':0,
                'quartos':quartos,
                'banheiros':0,
                'vagas':vagas,
                'anunciante':anunciante,
                'telefone':telefone,
                'area':area,
                'caracteristicas':caracteristicas,
                'data_cadastro':datetime.datetime.now(),
                "lat":lat,
                'lon':lon,
                'zipcode':zipcode
                }
            dados_imovel = pd.DataFrame(data,index=[0])
            
            #preços
            try:
                preco = utils.check_int(self.driver.find_element(By.CLASS_NAME,"js-price-rent").text)
            except:
                try:
                    preco = utils.check_int(self.driver.find_element(By.CLASS_NAME,"js-price-sale").text)
                except:
                    preco = -1
            try:
                preco_condominio = utils.check_int(self.driver.find_element(By.CLASS_NAME,"js-condominium").text)
            except:
                preco_condominio=-1
            try:
                iptu = utils.check_int(self.driver.find_element(By.CLASS_NAME,"js-iptu").text)
            except:
                iptu = -1
            ''
            data = {
                'id_imovel':row[0],
                'preco':preco,
                'condominio':preco_condominio,
                'iptu':iptu,
                "data_cadastro":datetime.datetime.now()}

            dados_preco = pd.DataFrame(data,index=[0])
            
            dados_fotos = pd.DataFrame()
            links=[]
            id_imovel=[]
            for photo in self.driver.find_elements(By.CLASS_NAME,"js-carousel-image"):
                url = photo.get_attribute("src")
                if 'resizedimgs' in url:
                    links.append(url)
                    id_imovel.append(row[0])

            dados_fotos["link"]=links
            dados_fotos['id_imovel']=id_imovel
            
            dados_preco.to_sql('precos',con=dbConnection,schema="viva_real",if_exists="append",index=False)
            dados_imovel.to_sql('imoveis',con=dbConnection,schema="viva_real",if_exists="append",index=False)                
            dados_fotos.to_sql('fotos',con=dbConnection,schema="viva_real",if_exists="append",index=False)

            time.sleep(2)

        logger.info(filename+'FINALIZADO')
        os.remove(filename) 
            
        return True 
        
    def quit(self):
        quit = self.driver.quit()
        return quit
    
    def fix_infos(self,info):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_server}/viva_real?password={self.db_pass}', pool_recycle=3600)
        dbConnection    = sqlEngine.connect()
        df = pd.read_sql("SELECT i.id,i.url FROM viva_real.imoveis i \
                        left join precos p ON p.id_imovel = i.id  where i.data_cadastro < '2022-12-13 15:50:13' limit 500",dbConnection)

        for index, row in df.iterrows():
            self.driver.get(row["url"])
            time.sleep(8)
            #preços
            try:
                infos_text=''
                while infos_text == '':
                    scripts=self.driver.find_elements(By.TAG_NAME,'script')
                    for i in scripts:
                        try:
                            if 'lat:' in i.get_attribute("innerHTML"):
                                infos_text = i.get_attribute("innerHTML")
                        except:
                            time.sleep(1)
                            pass
                try:
                    lat=infos_text.split("lat: ")[1].split("lon: ")[0].replace(",\n","").replace(" ","").replace("'","")
                    lon=infos_text.split("lon: ")[1].split("},")[0].replace(",\n","").replace(" ","").replace("'","")
                except:
                    lat=0
                    lon=0
                sql = f"""
                    UPDATE viva_real.imoveis
                    SET lat = {lat}, lon = {lon}
                    WHERE id = {row['id']}
                """
                print(sql)
                dbConnection.execute(sql)
                print(row['lat'],row['id'])
                print(f"    novo: {data}")

            except Exception as e:
                print(info,row['id'])
                pass
                # print(e)

        self.driver.quit()
        return True
