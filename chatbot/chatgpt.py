'''Class definition for ChatGPTClient'''

import logging
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as Exceptions

from .base_browser import BaseBrowser

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.WARNING
)

class ChatGPTClient(BaseBrowser):
    '''ChatGPTClient class to interact with ChatGPT'''

    login_xq    = '//button[//div[text()="Log in"]]'
    continue_xq = '//button[text()="Continue"]'
    tutorial_xq = '//div[contains(text(), "Okay, let’s go")]'
    button_tq   = 'button'
    done_xq     = '//button[//div[text()="Done"]]'

    menu_xq     = '//button[contains(@id, "headlessui-menu-button")]'
    custom_xq   = '//a[contains(text(), "Custom instructions")]'
    custom_toggle_xq    = '//button[@role="switch"]'
    custom_textarea_xq  = '//textarea[@type="button"]'
    custom_save_xq      = '//button[div[contains(text(), "Save")]]'
    custom_cancel_xq    = '//button[div[contains(text(), "Cancel")]]'
    custom_tutorial_xq  = '//div[text()="OK"]'

    chatbox_xq = '//div[@data-message-author-role="assistant"]'
    wait_xq     = '//button[@aria-label="Stop generating"]'
    reset_xq    = '//div[text()="New chat"]'
    reset_cq    = 'truncate'
    regen_xq    = '//button//div//*[name()="svg"]'
    textarea_tq = 'textarea'
    textarea_iq = 'prompt-textarea'
    gpt_xq    = '//span[text()="{}"]'

    def __init__(self, **kwargs):
        super().__init__(
            client_name='ChatGPT',
            url='https://chat.openai.com/auth/login?next=/chat',
            after_login_url='https://chat.openai.com/',
            uname_env_var='OPENAI_UNAME',
            pwd_env_var='OPENAI_PWD',
            **kwargs
        )

    def postload_custom_func(self):
        today_str = datetime.today().strftime('%Y-%m-%d')
        self.browser.execute_script(
            f"window.localStorage.setItem('oai/apps/hasSeenOnboarding/chat', {today_str});"
            f"window.localStorage.setItem('oai/apps/hasUserContextFirstTime/2023-06-29', true);"
            f"window.localStorage.setItem('oai/apps/announcement/customInstructions', 1694012515508);"
        )

    def pass_verification(self, max_trial : int = 10, wait_time : int = 1) -> bool:
        '''
        Performs the verification process on the page if challenge is present.

        This function checks if the login page is displayed in the browser.
        In that case, it looks for the verification button.
        This process is repeated until the login page is no longer displayed.

        Returns: None
        '''
        for _ in range(max_trial):
            if not self.check_login_page():
                break
            verify_button = self.browser.find_elements(By.ID, 'challenge-stage')
            if len(verify_button):
                try:
                    verify_button[0].click()
                    logging.info('Clicked verification button')
                except Exceptions.ElementNotInteractableException:
                    logging.info('Verification button is not present or clickable')
            time.sleep(wait_time)
        else:
            logging.error('It is not possible to pass verification')
            return False

        return True


    def is_challenge_page(self):
        '''
        Checks if the challenge page is displayed.

        This function checks if the challenge page is displayed in the browser.
        It returns True if the challenge page is displayed, False otherwise.

        Returns:
            bool: True if the challenge page is displayed, False otherwise.
        '''
        if "signin/challenge" in self.browser.current_url:
            return True
        
        challenge_texts = ["We've detected unusual activity", "Verify it's you"]
        for text in challenge_texts:
            if text in self.browser.page_source:
                return True   

        return False     
        

    def login_by_google(self, username : str, password : str):
        '''
        Performs the login process with the provided username and password via Google.

        This function operates on the login page. It finds and clicks the Google login button,
        fills in the email and password textboxes.

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            None
        '''
        # Find login button, click it
        login_button = self.sleepy_find_element(By.XPATH, self.login_xq)
        login_button.click()
        logging.info('Clicked login button')
        time.sleep(1)

        # Find and click the Google login button
        google_login_button = self.sleepy_find_element(By.CSS_SELECTOR, "button[data-provider='google']")
        google_login_button.click()
        time.sleep(1)

        # Find email textbox, enter e-mail
        email_box = self.sleepy_find_element(By.CSS_SELECTOR, "input[type='email']")
        email_box.send_keys(username)
        logging.info('Filled email box')
        time.sleep(1)

        # Click next button after email
        google_login_button = self.browser.find_elements(By.TAG_NAME, "button")[3]
        google_login_button.click()
        time.sleep(3)

        # Find password textbox, enter password
        try:
            self.sleepy_find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
        except Exception:
            self.sleepy_find_element(By.XPATH, '//input[@name="Passwd"]').send_keys(password)
        logging.info('Filled password box')
        time.sleep(3)

        # Click next button after password
        google_login_button = self.browser.find_elements(By.TAG_NAME, "button")[1]
        google_login_button.click()
        time.sleep(1)
        logging.info('Logged in with Google account')

        while self.is_challenge_page():
            time.sleep(1)

        try:
            # Additional steps if needed post-login
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, self.post_login_element_xq))
            ).click()
            logging.info('Post-login steps completed')
        except Exception as err:
            logging.error('Post-login error: %s', err)

    def login(self, username :str, password :str):
        '''
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            None
        '''

        # Find login button, click it
        login_button = self.sleepy_find_element(By.XPATH, self.login_xq)
        login_button.click()
        logging.info('Clicked login button')
        time.sleep(1)

        # Find email textbox, enter e-mail
        email_box = self.sleepy_find_element(By.ID, 'username')
        email_box.send_keys(username)
        logging.info('Filled email box')

        # Click continue
        continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)
        logging.info('Clicked continue button')

        # Find password textbox, enter password
        pass_box = self.sleepy_find_element(By.ID, 'password')
        pass_box.send_keys(password)
        logging.info('Filled password box')
        # Click continue
        pass_box.send_keys(Keys.ENTER)
        time.sleep(1)
        logging.info('Logged in')

        try:
            # Pass introduction
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, self.tutorial_xq))
            ).click()
            #next_button.find_elements(By.TAG_NAME, self.button_tq)[0].click()

            logging.info('Info screen passed')
        except Exceptions.TimeoutException:
            logging.info('Info screen skipped')
        except Exception as err:
            logging.error('Something unexpected has happened: %s', err)

        if not self.check_login_success_condition():
            self.wait_login_manully()

    def wait_login_manully(self, timeout=100):
        '''
        Waits for a manual action to be completed.

        Args:
            driver: The WebDriver instance.
            timeout: Maximum time to wait (in seconds) before timing out.
            check_condition_func: Function that checks if the condition for resuming automation is met.
        '''
        try: 
            WebDriverWait(self.browser, timeout).until(
                lambda driver: self.check_login_success_condition()
            )
            logging.info('Login process is completed manually')
        except TimeoutError:
            logging.error('Login process is not completed manually')

    def check_login_success_condition(self):
        return "login" not in self.browser.current_url and "auth" not in self.browser.current_url and "error" not in self.browser.current_url and "chat.openai.com" in self.browser.current_url


    def interact(self, question : str):
        '''
        Sends a question and retrieves the answer from the ChatGPT system.

        This function interacts with the ChatGPT.
        It takes the question as input and sends it to the system.
        The question may contain multiple lines separated by '\n'. 
        In this case, the function simulates pressing SHIFT+ENTER for each line.

        After sending the question, the function waits for the answer.
        Once the response is ready, the response is returned.

        Args:
            question (str): The interaction text.

        Returns:
            str: The generated answer.
        '''

        text_area = self.browser.find_elements(By.TAG_NAME, self.textarea_tq)
        if not text_area:
            logging.info('Unable to locate text area tag. Switching to ID search')
            text_area = self.browser.find_elements(By.ID, self.textarea_iq)
        if not text_area:
            raise RuntimeError(
                'Unable to find the text prompt area. Please raise an issue with verbose=True')

        text_area = text_area[0]

        for each_line in question.split('\n'):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        logging.info('Message sent, waiting for response')
        self.wait_until_disappear(By.XPATH, self.wait_xq)
        if self.target_url is not None:
            time.sleep(30)
        else:
            time.sleep(1)
        answer = self.find_or_fail(By.XPATH, self.chatbox_xq, return_type='last')
        if not answer:
            logging.error('There is no answer, something is wrong')
            return ''

        logging.info('Answer is ready')
        self.save_turn(question=question, answer=answer.text)

        return answer.text

    def reset_thread(self):
        '''Function to close the current thread and start new one'''
        try:
            self.browser.find_element(By.XPATH, self.reset_xq).click()
        except Exceptions.NoSuchElementException:
            logging.info('New Chat button is not available, dropping to class search')
            new_button = self.find_or_fail(By.CLASS_NAME, self.reset_cq, return_type='first')
            if not new_button:
                logging.info('There is no button to click')
                return False
            try:
                new_button.click()
                logging.info('Clicked the button')
            except (IndexError, Exceptions.ElementNotInteractableException) as err:
                logging.error(
                    '%s. '
                    'It seems UI has changed.'
                    'Please raise an issue after running the constructor with verbose=True',
                    err
                )
                return False
        logging.info('New thread is ready')
        return True

    def regenerate_response(self):
        '''
        Closes the current thread and starts a new one.

        Args:
            None

        Returns:
            None
        '''
        regen_button = self.find_or_fail(By.XPATH, self.regen_xq, return_type='last')
        if not regen_button:
            return None

        regen_button.click()
        logging.info('Clicked regenerate button')
        self.wait_until_disappear(By.XPATH, self.wait_xq)
        answer = self.find_or_fail(By.XPATH, self.chatbox_xq, return_type='last')
        if not answer:
            logging.error('Regenerated answer is not present')
            return ''

        logging.info('New answer is ready')
        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = ['chatgpt', True, answer.text]
        return answer.text

    def switch_model(self, model_name : str):
        '''
        Switch the model for ChatGPT+ users.

        Args:
            model_name: str = The name of the model, either GPT-3.5 or GPT-4

        Returns:
            bool: True on success, False on fail
        '''
        if model_name in ['GPT-3.5', 'GPT-4']:
            logging.info('Switching model to %s', model_name)
            try:
                self.browser.find_element(By.XPATH, self.gpt_xq.format(model_name)).click()
                return True
            except Exceptions.NoSuchElementException:
                logging.error('Button is not present')
        else:
            logging.error('Model name is not ')
        return False

    def open_custom_instruction_tab(self):
        """Opens the modal to access custom interactions. 

        Returns:
            bool: True if the process is successful, False otherwise
        """

        menu_button = self.find_or_fail(By.XPATH, self.menu_xq)
        menu_button.click()
        custom_button = self.find_or_fail(By.XPATH, self.custom_xq)
        custom_button.click()
        custom_tutorial = self.find_or_fail(By.XPATH, self.custom_tutorial_xq, fail_ok=True)
        if custom_tutorial:
            custom_tutorial.click()

        custom_switch = self.find_or_fail(By.XPATH, self.custom_toggle_xq)
        if not custom_switch:
            return False

        # If disabled, enable custom interactions
        if custom_switch.get_attribute('data-state') == 'checked':
            logging.info('Custom instructions is enabled')
        else:
            custom_switch.click()
        time.sleep(0.2)

        return True

    def get_custom_instruction(self, mode: str):
        """Gets custom instructions

        Args:
            mode (str): Either 'extra_information' or 'modulation'. Check OpenAI help pages.
        """
        if not self.open_custom_instruction_tab():
            return None
        text_areas = self.find_or_fail(By.XPATH, self.custom_textarea_xq, return_type='all')
        text = text_areas[{
            'extra_information' : 0,
            'modulation' : 1
        }[mode]].text
        logging.info('Custom instruction is obtained: %s', text)

        save_button = self.find_or_fail(By.XPATH, self.custom_cancel_xq)
        save_button.click()
        return text

    def set_custom_instruction(self, mode: str, instruction: str):
        """Sets custom instructions

        Args:
            mode (str): Either 'extra_information' or 'modulation'. Check OpenAI help pages.
            instruction (str): _description_
        """
        if not self.open_custom_instruction_tab():
            return False

        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, self.custom_textarea_xq))
        )
        text_areas = self.find_or_fail(By.XPATH, self.custom_textarea_xq, return_type='all')
        text_area = text_areas[{
            'extra_information' : 0,
            'modulation' : 1
        }[mode]]

        text_area.send_keys(Keys.CONTROL + "a")
        time.sleep(0.1)
        text_area.send_keys(Keys.DELETE)
        time.sleep(0.1)
        text_area.send_keys(instruction)
        time.sleep(0.1)
        logging.info('Custom instruction-%s has provided', mode)

        save_button = self.find_or_fail(By.XPATH, self.custom_save_xq)
        save_button.click()
        return True