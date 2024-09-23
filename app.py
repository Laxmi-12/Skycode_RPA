import os
import platform
from flask import Flask, request, jsonify
import json
import logging
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException,NoSuchWindowException,NoSuchElementException,ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from flask_cors import CORS ,  cross_origin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomationSetting:
    """This class handles the setup, navigation, and interaction with web pages using Selenium WebDriver."""

    driver = None  # Class-level variable to hold the WebDriver instance
    @staticmethod
    def capture_screenshot(step_name):
        """Capture screenshot and save it with a unique name."""
        logger.info(f"Capture screenshot and save it with a unique name.")
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f"{step_name}_{timestamp}.png")
        
        try:
            if AutomationSetting.driver:
                AutomationSetting.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot captured and saved to {screenshot_path}")
            else:
                raise NoSuchWindowException("WebDriver instance is not available.")
        except NoSuchWindowException as nwe:
            error_message = (f"Error capturing screenshot: WebDriver window is closed or not available - {nwe.msg}")
            logger.error(error_message)
            raise
        except WebDriverException as wde:
            error_message = (f"Error capturing screenshot: WebDriver exception - {wde.msg}")
            logger.error(error_message)
            raise
        except Exception as e:
            error_message = (f"Unexpected error capturing screenshot: {e}")
            logger.error(error_message)
            raise

        return screenshot_path

    @staticmethod
    def is_aws_environment():
        """Determine if the current environment is AWS."""
        # You can use different methods to check if it's an AWS environment
        # Here's an example using the hostname or an environment variable
        return os.getenv("AWS_EXECUTION_ENV") is not None or "EC2" in platform.node()

    @staticmethod
    def initialize_driver(form_status):
        """Initialize the WebDriver and store it as a class attribute."""
        if AutomationSetting.driver is None:
            try:
                logger.info("Installing ChromeDriver using ChromeDriverManager...")
                driver_path = ChromeDriverManager().install()
                if not driver_path.endswith("chromedriver.exe"):
                    driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe")
                logger.info(f"ChromeDriver installed at: {driver_path}")

                logger.info("Initializing Chrome WebDriver...")
                # Set Chrome options
                chrome_options = Options()

                if AutomationSetting.is_aws_environment():
                    logger.info("Running in AWS environment")
                    chrome_options.binary_location = "/usr/bin/google-chrome"
                    # AWS-specific options
                    chrome_options.add_argument("--headless")
                else:
                    logger.info("Running in local environment")
                    # Dynamically determine the Chrome binary location for local
                    if platform.system() == "Windows":
                        chrome_path = ("C:/Program Files/Google/Chrome/Application/chrome.exe")
                    elif platform.system() == "Darwin":  # macOS
                        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                    else:  # Assume Linux
                        chrome_path = "/usr/bin/google-chrome"

                    if os.path.exists(chrome_path):
                        chrome_options.binary_location = chrome_path
                    else:
                        raise FileNotFoundError(f"Chrome binary not found at {chrome_path}")

                # Common Chrome options
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")

                s = Service(executable_path=driver_path)
                AutomationSetting.driver = webdriver.Chrome(service=s, options=chrome_options)
                AutomationSetting.driver.maximize_window()
                logger.info("WebDriver initialized successfully.")
                form_status["initialized"] = True  # Update form_status
            except WebDriverException as wde:
                form_status["error"] = (f"Error initializing WebDriver: {wde.msg}")
                logger.error(form_status["error"])
                raise
            except Exception as e:
                form_status["error"] = f"Error initializing WebDriver: {e}"
                logger.error(form_status["error"])
                raise

    @staticmethod
    def navigate_to(url, form_status):
        """Navigate to the specified URL."""
        try:
            if AutomationSetting.driver is not None:
                AutomationSetting.driver.get(url)
                # AutomationSetting.capture_screenshot("navigated_to_url")
                logger.info(f"Navigated to URL: {url}")
            form_status["navigated"] = True  # Update form_status

        except WebDriverException as wde:
            form_status["error"] = f"Error navigating to URL {url}: {wde.msg}"
            logger.error(form_status["error"])
            raise

    @staticmethod
    def close_driver(form_status):
        """Close the WebDriver."""
        try:
            if AutomationSetting.driver is not None:
                # AutomationSetting.capture_screenshot("before_closing_driver")
                AutomationSetting.driver.quit()
                AutomationSetting.driver = None
                logger.info("WebDriver closed successfully.")
                form_status["initialized"] = True  # Update form_status
        except NoSuchWindowException as nwe:
            form_status["error"] = (f"Error closing WebDriver: {nwe.msg}")
            logger.error(form_status["error"])
            raise
        except WebDriverException as wde:
            form_status["error"] = (f"Error closing WebDriver: {wde.msg}")
            logger.error(form_status["error"])
            raise

    @staticmethod
    def setting(url, forms, input_data, form_status):
        """Set up the WebDriver, navigate to the login URL, and fill the forms."""
        get_element_result = []
        success = False
        try:
            AutomationSetting.initialize_driver(form_status)
            AutomationSetting.navigate_to(url, form_status)
            WebDriverWait(AutomationSetting.driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            processed_forms_count = 0
            for form in forms:
                try:
                    form_values = {fv['field_id']: {'value': fv['value'], 'value_type': fv.get('value_type')} for fv in form.get('form_value', [])}
                    element_details = {el['efield_id']: {'evalue': el['evalue'],'evalue_type': el.get('evalue_type'),'eaction': el['eaction']} for el in form['form_element_details']}
                    
                    form_status, get_element_result = AutomationSetting.fill_form(form_values, element_details, input_data, form_status, get_element_result)
                    sleep(2) 

                    processed_forms_count += 1
                    form_status["processed_forms_count"] = processed_forms_count
                    logger.info(f"Processed {processed_forms_count} forms successfully for URL: {url}")

                except KeyError as ke:
                    form_status["error"] = f"Missing key in form data: {ke}"
                    logger.error(form_status["error"])
                    raise ValueError(form_status["error"])
                except Exception as e:
                    form_status["error"] = (f"An error occurred while processing the form: {e}")
                    logger.error(form_status["error"])
                    raise ValueError(form_status["error"])


            WebDriverWait(AutomationSetting.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            success = True
        except ValueError as e:
            form_status["error"] = f"Validation error: {e}"
            logger.error(form_status["error"])
            raise
        except Exception as e:
            form_status["error"] = f"An error occurred during the setting process: {e.msg}"
            logger.error(form_status["error"])
            raise
        finally:
            AutomationSetting.close_driver(form_status)
            if success == True:
                form_status["error"] = False
                return {"message": "RPA process started successfully","element_result": get_element_result, "form_status": form_status}
            else:
                return {"element_result": get_element_result, "form_status": form_status}

    @staticmethod
    def fill_form(form_values, element_details, input_data, form_status, get_element_result):
        """Fill the form using the provided API configuration and input data."""
        for form_field_id, details in element_details.items():
            try:
                evalue = details["evalue"]
                evalue_type = details["evalue_type"]
                eaction = details["eaction"]
                logger.info(f"Locating element '{form_field_id}' using {evalue_type}: {evalue}")
                retries = 3  # Number of retries for stale element
                while retries > 0:
                    try:
                        element = None
                        # Determine the appropriate locator based on evalue_type
                        if evalue_type == "XPATH":
                            locator = (By.XPATH, evalue)
                        elif evalue_type == "ID":
                            locator = (By.ID, evalue)
                        elif evalue_type == "CLASS_NAME":
                            locator = (By.CLASS_NAME, evalue)
                        elif evalue_type == "CSS_SELECTOR":
                            locator = (By.CSS_SELECTOR, evalue)
                        elif evalue_type == "NAME":
                            locator = (By.NAME, evalue)
                        else:
                            form_status["updated"] = False
                            form_status["processed_forms_count"] += 1
                            form_status["error"] = f"Unsupported locator type '{evalue_type}' for '{form_field_id}'."
                            logger.error(form_status["error"])
                            raise ValueError(form_status["error"])

                        if locator:
                            conditions = [
                                EC.visibility_of_element_located(locator),
                                # EC.presence_of_element_located(locator),
                                # EC.presence_of_nested_elements_located_by(locator),
                                # EC.attribute_to_be((By.CSS_SELECTOR, '[data-testid="org-user-list-more-details-button"]'), "aria-expanded", "true"),
                                EC.element_to_be_clickable(locator)
                            ]
                        elements =WebDriverWait(AutomationSetting.driver, 100).until(EC.any_of(*conditions))

                        # If `elements` is a tuple or list, handle it accordingly
                        if isinstance(elements, tuple) or isinstance(elements, list):
                            for el in elements:
                                print(el)
                                if el.is_displayed():
                                    element = el
                                    break
                        else:
                            element = elements


                        if element:
                            
                            if eaction == "send_keys":
                                element.clear()
                                if form_field_id in form_values:
                                    form_value = form_values[form_field_id]
                                    value = form_value["value"]
                                    value_type = form_value["value_type"]

                                    if value_type == "value":
                                        logger.info(f"Filling value for '{form_field_id}' with value: {value}")
                                        element.send_keys(value)
                                    elif value_type == "field_id":
                                        input_field_id = value
                                        input_value = None
                                        for data in input_data:
                                            if input_field_id in data:
                                                input_value = data[input_field_id]
                                                break
                                        if input_value:
                                            logger.info(f"Filling value for '{form_field_id}' with value from input_data: {input_value}")
                                            element.send_keys(input_value)
                                        else:
                                            form_status["updated"] = False
                                            form_status["processed_forms_count"] += 1
                                            form_status["error"] = f"No value found for '{input_field_id}' in API response."
                                            logger.error(form_status["error"])
                                            raise ValueError(form_status["error"])
                                           
                                    else:
                                        form_status["updated"] = False
                                        form_status["processed_forms_count"] += 1
                                        form_status["error"] = f"Unsupported value type '{value_type}' for '{form_field_id}'"
                                        logger.error(form_status["error"])
                                        raise ValueError(form_status["error"])

                            elif eaction == "date_send_keys":
                                element.clear()
                                if form_field_id in form_values:
                                    form_value = form_values[form_field_id]
                                    value = form_value["value"]
                                    value_type = form_value["value_type"]

                                    if value_type == "value":
                                        logger.info(f"Filling value for '{form_field_id}' with value: {value}")
                                        element.send_keys(value)
                                    elif value_type == "field_id":
                                        input_field_id = value
                                        input_value = None
                                        for data in input_data:
                                            if input_field_id in data:
                                                input_value = data[input_field_id]
                                                break
                                        if input_value:
                                            # Convert to datetime object
                                            dt = datetime.strptime(input_value, "%Y-%m-%dT%H:%M:%S.%f")
                                            formatted_date = dt.strftime("%m-%d-%Y")
                                            logger.info(f"Filling value for '{form_field_id}' with value from input_data: {formatted_date}")
                                            element.send_keys(formatted_date)
                                        else:
                                            form_status["updated"] = False
                                            form_status["processed_forms_count"] += 1
                                            form_status["error"] = f"No value found for '{input_field_id}' in API response."
                                            logger.error(form_status["error"])
                                            break
                                    else:
                                        form_status["updated"] = False
                                        form_status["processed_forms_count"] += 1
                                        form_status["error"] = f"Unsupported value type '{value_type}' for '{form_field_id}'."
                                        logger.error(form_status["error"])
                                        break
                            
                            elif eaction == "click":
                                logger.info(f"Clicking button '{form_field_id}'")
                                element.click()

                            elif eaction == "wait_click":
                                sleep(30)
                                logger.info(f"Waiting for '{form_field_id}' action. Timeout in 30 seconds.")
                                element.click()

                            elif eaction == "wait_loading":
                                sleep(30)
                                logger.info(f"Waiting for loading completion.")
                            elif eaction == "switch_to_iframe":
                                AutomationSetting.driver.switch_to.frame(element)
                                logger.info(f"Switched to iframe '{form_field_id}'")

                            elif eaction == "switch_to_window":
                                window_handles = AutomationSetting.driver.window_handles
                                AutomationSetting.driver.switch_to.window(window_handles[1])
                                logger.info("Switched to new window.")

                            elif eaction == "clear":
                                element.clear()
                                logger.info(f"Cleared input for '{form_field_id}'.")

                            elif eaction == "get_element_text":
                                extracted_text = element.text
                                logger.info(f"Extracted element text '{extracted_text}'")
                                #print("get element ----*******----------",form_values)
                                if form_field_id in form_values:
                                    form_value = form_values[form_field_id]
                                    value = form_value["value"]
                                    value_type = form_value["value_type"]
                                    get_element_result.append({"field_id": form_field_id,"value": extracted_text,"value_type": value_type})
                                    #print("get_element_result=============",get_element_result)
                                    logger.info(f"Processed text for '{form_field_id}': '{extracted_text}'")
                                else:
                                    form_status["updated"] = False
                                    form_status["processed_forms_count"] += 1
                                    form_status["error"] = f"Form values is empty"
                                    logger.error(form_status["error"])
                                    raise ValueError(form_status["error"])
                            else:
                                form_status["updated"] = False
                                form_status["processed_forms_count"] += 1
                                form_status["error"] = f"Unsupported action '{eaction}' for '{form_field_id}'. "
                                logger.error(form_status["error"])
                                raise ValueError(form_status["error"])

                            form_status["updated"] = True
                            form_status["processed_forms_count"] += 1
                            logger.info(f"Performed action '{eaction}' on element '{form_field_id}' successfully.")
                            break  # Break out of retry loop if successful
                        else:
                            logger.error(f"Failed to locate element '{form_field_id}' after retries.")
                            form_status["error"] = f"Timeout occurred while locating element 1'{form_field_id}'"
                            raise TimeoutException(form_status["error"])
                
                    except StaleElementReferenceException as sere:
                        logger.warning(f"StaleElementReferenceException encountered. Retrying... ({retries} retries left)")
                        retries -= 1
                        sleep(2)  # Small delay before retrying
            except TimeoutException as te:
                form_status["error"] = (f"Timeout occurred while locating element  2'{form_field_id}': {te.msg}")
                logger.error(form_status["error"])
                # return form_status, get_element_result
                raise ValueError(form_status["error"])
            except NoSuchWindowException as nwe:
                form_status["error"] = f"NoSuchWindowException occurred: {nwe.msg}"
                logger.error(form_status["error"])
                # return form_status, get_element_result
                raise ValueError(form_status["error"])
            except NoSuchElementException as nse:
                form_status["error"] = f"NoSuchElementException occurred: {nse.msg}"
                logger.error(form_status["error"])
                # return form_status, get_element_result
                raise ValueError(form_status["error"])

            except ElementNotInteractableException as ent:
                form_status["error"] = f"ElementNotInteractableException occurred: {ent.msg}"
                logger.error(form_status["error"])
                # return form_status, get_element_result
                raise ValueError(form_status["error"])
            except WebDriverException as wde:
                form_status["error"] = (f"WebDriverException occurred while processing element '{form_field_id}': {wde.msg}")
                logger.error(form_status["error"])
                # return form_status, get_element_result
                raise ValueError(form_status["error"])
            except Exception as e:
                form_status["error"] = f"An unexpected error occurred: {e}"
                logger.error(form_status["error"])
                # return form_status, get_element_result
                raise ValueError(form_status["error"])
        return form_status, get_element_result
    


app = Flask(__name__)
CORS(app, resources={r"/start-rpa": {"origins": "*"}})  # Allow all origins
# CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello Welcome to RPA</p>"

# Define a POST endpoint to receive a name
@app.route("/start-rpa", methods=["POST"])
@cross_origin()



def submit_name():
    logger.info("Received a new request in AutomationView")
    form_status_view = {"error": None}
    try:
        # Get the JSON data from the request
        data = request.get_json()
        print(data)
        config = data.get('config', None)
        schema_config = config['schema_config']
        input_data = config['input_data']

        # Validate the `schema_config` and ensure `form_status` exists
        if not schema_config or not schema_config[0].get("form_status"):
            form_status_view["error"] = "Invalid schema_config or form_status missing"
            logger.error(form_status_view["error"])
            return jsonify(form_status_view), 400

        # Additional validation for input_data if necessary
        if not input_data:
            form_status_view["error"] = "Input data is missing"
            logger.error(form_status_view["error"])
            return jsonify(form_status_view), 400

        logger.info(f"Input data: {input_data}")

        # Extract URL, forms, and form_status from schema_config
        url = schema_config[0].get("url")
        forms = schema_config[0].get("forms")
        form_status = schema_config[0].get("form_status")[0]

        logger.info(f"Form status: {form_status}")
        logger.info(f"Processing URL: {url}")

        # Assuming `AutomationSetting.setting` is the function handling automation
        result_setting = AutomationSetting.setting(url, forms, input_data, form_status)

        logger.info(f"Result from setting: {result_setting}")
       
        # Check if any error occurred during form submission
        form_error_status = result_setting.get('form_status', {}).get('error', None)
        # print(form_error_status)
        if form_error_status is False:
            logger.info("Successfully processed the request")
            return jsonify(result_setting), 200
        else:
            logger.error({"error": "An error occurred during RPA processing","details": form_error_status})
            return jsonify({"error": "An error occurred during RPA processing","details": form_error_status}), 400

    # Handle JSON decoding errors
    except ValueError as ve:
        form_status_view["error"] = f"Value error: {ve}"
        logger.error(form_status_view["error"], exc_info=True)
        return jsonify(form_status_view), 400

    # Handle missing keys in the data
    except KeyError as e:
        form_status_view["error"] = f"{e.args[0]} is missing"
        logger.error(form_status_view["error"], exc_info=True)
        return jsonify(form_status_view), 400

    # Catch all other exceptions
    except Exception as e:
        form_status_view["error"] = f"An error occurred while processing: {e}"
        logger.error(form_status_view["error"], exc_info=True)
        return jsonify(form_status_view), 500
    
if __name__ == "__main__":
    app.run(debug=True)