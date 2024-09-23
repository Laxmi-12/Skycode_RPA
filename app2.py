T='/start-rpa'
R='initialized'
s=print
r=isinstance
Q=KeyError
k='eaction'
j='evalue_type'
i='evalue'
f='field_id'
X='value_type'
W=Exception
C=staticmethod
N='value'
L='processed_forms_count'
K=False
J=True
H=None
F=ValueError
A='error'
import os as G,platform as M
from flask import Flask,request as Y,jsonify as D
import json,logging as O
from time import sleep as a
from datetime import datetime as p
from selenium import webdriver as U
from selenium.webdriver.common.by import By as S
from selenium.webdriver.chrome.service import Service as V
from selenium.webdriver.support.ui import WebDriverWait as h
from selenium.webdriver.support import expected_conditions as b
from webdriver_manager.chrome import ChromeDriverManager as P
from selenium.common.exceptions import TimeoutException as q,WebDriverException as c,StaleElementReferenceException as w,NoSuchWindowException as e,NoSuchElementException as x,ElementNotInteractableException as y
from selenium.webdriver.chrome.options import Options as Z
from time import sleep as a
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager as P
from flask_cors import CORS,cross_origin as d
O.basicConfig(level=O.INFO)
B=O.getLogger(__name__)
class E:
	driver=H
	@C
	def capture_screenshot(step_name):
		B.info(f"Capture screenshot and save it with a unique name.");D=G.path.join(G.getcwd(),'screenshots');G.makedirs(D,exist_ok=J);F=p.now().strftime('%Y%m%d%H%M%S');C=G.path.join(D,f"{step_name}_{F}.png")
		try:
			if E.driver:E.driver.save_screenshot(C);B.info(f"Screenshot captured and saved to {C}")
			else:raise e('WebDriver instance is not available.')
		except e as H:A=f"Error capturing screenshot: WebDriver window is closed or not available - {H.msg}";B.error(A);raise
		except c as I:A=f"Error capturing screenshot: WebDriver exception - {I.msg}";B.error(A);raise
		except W as K:A=f"Unexpected error capturing screenshot: {K}";B.error(A);raise
		return C
	@C
	def is_aws_environment():return G.getenv('AWS_EXECUTION_ENV')is not H or'EC2'in M.node()
	@C
	def initialize_driver(form_status):
		L='/usr/bin/google-chrome';K='chromedriver.exe';D=form_status
		if E.driver is H:
			try:
				B.info('Installing ChromeDriver using ChromeDriverManager...');F=P().install()
				if not F.endswith(K):F=F.replace('THIRD_PARTY_NOTICES.chromedriver',K)
				B.info(f"ChromeDriver installed at: {F}");B.info('Initializing Chrome WebDriver...');C=Z()
				if E.is_aws_environment():B.info('Running in AWS environment');C.binary_location=L;C.add_argument('--headless')
				else:
					B.info('Running in local environment')
					if M.system()=='Windows':I='C:/Program Files/Google/Chrome/Application/chrome.exe'
					elif M.system()=='Darwin':I='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
					else:I=L
					if G.path.exists(I):C.binary_location=I
					else:raise FileNotFoundError(f"Chrome binary not found at {I}")
				C.add_argument('--disable-gpu');C.add_argument('--no-sandbox');C.add_argument('--disable-dev-shm-usage');N=V(executable_path=F);E.driver=U.Chrome(service=N,options=C);E.driver.maximize_window();B.info('WebDriver initialized successfully.');D[R]=J
			except c as O:D[A]=f"Error initializing WebDriver: {O.msg}";B.error(D[A]);raise
			except W as Q:D[A]=f"Error initializing WebDriver: {Q}";B.error(D[A]);raise
	@C
	def navigate_to(url,form_status):
		D=form_status;C=url
		try:
			if E.driver is not H:E.driver.get(C);B.info(f"Navigated to URL: {C}")
			D['navigated']=J
		except c as F:D[A]=f"Error navigating to URL {C}: {F.msg}";B.error(D[A]);raise
	@C
	def close_driver(form_status):
		C=form_status
		try:
			if E.driver is not H:E.driver.quit();E.driver=H;B.info('WebDriver closed successfully.');C[R]=J
		except e as D:C[A]=f"Error closing WebDriver: {D.msg}";B.error(C[A]);raise
		except c as F:C[A]=f"Error closing WebDriver: {F.msg}";B.error(C[A]);raise
	@C
	def setting(url,forms,input_data,form_status):
		M='body';C=form_status;H=[];O=K
		try:
			E.initialize_driver(C);E.navigate_to(url,C);h(E.driver,100).until(b.presence_of_element_located((S.TAG_NAME,M)));G=0
			for I in forms:
				try:P={A[f]:{N:A[N],X:A.get(X)}for A in I.get('form_value',[])};R={A['efield_id']:{i:A[i],j:A.get(j),k:A[k]}for A in I['form_element_details']};C,H=E.fill_form(P,R,input_data,C,H);a(2);G+=1;C[L]=G;B.info(f"Processed {G} forms successfully for URL: {url}")
				except Q as T:C[A]=f"Missing key in form data: {T}";B.error(C[A]);raise F(C[A])
				except W as D:C[A]=f"An error occurred while processing the form: {D}";B.error(C[A]);raise F(C[A])
			h(E.driver,30).until(b.presence_of_element_located((S.TAG_NAME,M)));O=J
		except F as D:C[A]=f"Validation error: {D}";B.error(C[A]);raise
		except W as D:C[A]=f"An error occurred during the setting process: {D.msg}";B.error(C[A]);raise
		finally:E.close_driver(C)
	@C
	def fill_form(form_values,element_details,input_data,form_status,get_element_result):
		u=get_element_result;t=input_data;Y=form_values;R='updated';C=form_status
		for(D,l)in element_details.items():
			try:
				Z=l[i];T=l[j];I=l[k];B.info(f"Locating element '{D}' using {T}: {Z}");m=3
				while m>0:
					try:
						G=H
						if T=='XPATH':U=S.XPATH,Z
						elif T=='ID':U=S.ID,Z
						elif T=='CLASS_NAME':U=S.CLASS_NAME,Z
						elif T=='CSS_SELECTOR':U=S.CSS_SELECTOR,Z
						elif T=='NAME':U=S.NAME,Z
						else:C[R]=K;C[L]+=1;C[A]=f"Unsupported locator type '{T}' for '{D}'.";B.error(C[A]);raise F(C[A])
						if U:z=[b.visibility_of_element_located(U),b.element_to_be_clickable(U)]
						g=h(E.driver,100).until(b.any_of(*z))
						if r(g,tuple)or r(g,list):
							for n in g:
								s(n)
								if n.is_displayed():G=n;break
						else:G=g
						if G:
							if I=='send_keys':
								G.clear()
								if D in Y:
									O=Y[D];P=O[N];M=O[X]
									if M==N:B.info(f"Filling value for '{D}' with value: {P}");G.send_keys(P)
									elif M==f:
										V=P;Q=H
										for d in t:
											if V in d:Q=d[V];break
										if Q:B.info(f"Filling value for '{D}' with value from input_data: {Q}");G.send_keys(Q)
										else:C[R]=K;C[L]+=1;C[A]=f"No value found for '{V}' in API response.";B.error(C[A]);raise F(C[A])
									else:C[R]=K;C[L]+=1;C[A]=f"Unsupported value type '{M}' for '{D}'";B.error(C[A]);raise F(C[A])
							elif I=='date_send_keys':
								G.clear()
								if D in Y:
									O=Y[D];P=O[N];M=O[X]
									if M==N:B.info(f"Filling value for '{D}' with value: {P}");G.send_keys(P)
									elif M==f:
										V=P;Q=H
										for d in t:
											if V in d:Q=d[V];break
										if Q:A0=p.strptime(Q,'%Y-%m-%dT%H:%M:%S.%f');v=A0.strftime('%m-%d-%Y');B.info(f"Filling value for '{D}' with value from input_data: {v}");G.send_keys(v)
										else:C[R]=K;C[L]+=1;C[A]=f"No value found for '{V}' in API response.";B.error(C[A]);break
									else:C[R]=K;C[L]+=1;C[A]=f"Unsupported value type '{M}' for '{D}'.";B.error(C[A]);break
							elif I=='click':B.info(f"Clicking button '{D}'");G.click()
							elif I=='wait_click':a(30);B.info(f"Waiting for '{D}' action. Timeout in 30 seconds.");G.click()
							elif I=='wait_loading':a(30);B.info(f"Waiting for loading completion.")
							elif I=='switch_to_iframe':E.driver.switch_to.frame(G);B.info(f"Switched to iframe '{D}'")
							elif I=='switch_to_window':A1=E.driver.window_handles;E.driver.switch_to.window(A1[1]);B.info('Switched to new window.')
							elif I=='clear':G.clear();B.info(f"Cleared input for '{D}'.")
							elif I=='get_element_text':
								o=G.text;B.info(f"Extracted element text '{o}'")
								if D in Y:O=Y[D];P=O[N];M=O[X];u.append({f:D,N:o,X:M});B.info(f"Processed text for '{D}': '{o}'")
								else:C[R]=K;C[L]+=1;C[A]=f"Form values is empty";B.error(C[A]);raise F(C[A])
							else:C[R]=K;C[L]+=1;C[A]=f"Unsupported action '{I}' for '{D}'. ";B.error(C[A]);raise F(C[A])
							C[R]=J;C[L]+=1;B.info(f"Performed action '{I}' on element '{D}' successfully.");break
						else:B.error(f"Failed to locate element '{D}' after retries.");C[A]=f"Timeout occurred while locating element 1'{D}'";raise q(C[A])
					except w as A8:B.warning(f"StaleElementReferenceException encountered. Retrying... ({m} retries left)");m-=1;a(2)
			except q as A2:C[A]=f"Timeout occurred while locating element  2'{D}': {A2.msg}";B.error(C[A]);raise F(C[A])
			except e as A3:C[A]=f"NoSuchWindowException occurred: {A3.msg}";B.error(C[A]);raise F(C[A])
			except x as A4:C[A]=f"NoSuchElementException occurred: {A4.msg}";B.error(C[A]);raise F(C[A])
			except y as A5:C[A]=f"ElementNotInteractableException occurred: {A5.msg}";B.error(C[A]);raise F(C[A])
			except c as A6:C[A]=f"WebDriverException occurred while processing element '{D}': {A6.msg}";B.error(C[A]);raise F(C[A])
			except W as A7:C[A]=f"An unexpected error occurred: {A7}";B.error(C[A]);raise F(C[A])
		return C,u
I=Flask(__name__)
CORS(I,resources={T:{'origins':'*'}})
@I.route('/')
def g():return'<p>Hello Welcome to RPA</p>'
@I.route(T,methods=['POST'])
@d()
def l():
	V='An error occurred during RPA processing';U='details';O='form_status';B.info('Received a new request in AutomationView');C={A:H}
	try:
		P=Y.get_json();s(P);R=P.get('config',H);G=R['schema_config'];I=R['input_data']
		if not G or not G[0].get(O):C[A]='Invalid schema_config or form_status missing';B.error(C[A]);return D(C),400
		if not I:C[A]='Input data is missing';B.error(C[A]);return D(C),400
		B.info(f"Input data: {I}");S=G[0].get('url');X=G[0].get('forms');T=G[0].get(O)[0];B.info(f"Form status: {T}");B.info(f"Processing URL: {S}");L=E.setting(S,X,I,T);B.info(f"Result from setting: {L}");M=L.get(O,{}).get(A,H)
		if M is K:B.info('Successfully processed the request');return D(L),200
		else:B.error({A:V,U:M});return D({A:V,U:M}),400
	except F as Z:C[A]=f"Value error: {Z}";B.error(C[A],exc_info=J);return D(C),400
	except Q as N:C[A]=f"{N.args[0]} is missing";B.error(C[A],exc_info=J);return D(C),400
	except W as N:C[A]=f"An error occurred while processing: {N}";B.error(C[A],exc_info=J);return D(C),500
if __name__=='__main__':I.run(debug=J)