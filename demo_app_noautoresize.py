import flet as ft 
import firebase_handler as fh 
import colours 

from concurrent.futures import ThreadPoolExecutor 

import sys 
sys.setrecursionlimit(1000010) # just to make sure that we don't accidentally hit recursion limit with too many login/logouts 
# TODO maybe we should optimize it such that we don't need it to go recursively?? 

current_user = None 

# so that debugs can easily be deleted 
def debug_print(*args, **kwargs): 
    print(*args, **kwargs) 



# login logout and dashboard ----------------------------------------------------------------------------------------------------------------
# TODO: allow forget password / password reset or smtg, maybe enable more login options 

# login page
def login_page(page:ft.Page, nextpage, email_onchange=lambda x:None, password_onchance=lambda x:None, clean_page=True):
    debug_print("LOGIN PAGE") 

    if clean_page: 
        page.clean() # in case we're coming from another page, clear the page 

    
    # header text 
    
    appname_label = ft.Text("Freelance Nursing!!", max_lines=1, size=min(page.window.height//20, page.window.width//10)) # 5% of screen height 
    # TOOD verify this will always fit 
    

    # first kind of UI for input 
    email_label = ft.Text('Email: ') 
    email_in = ft.TextField(hint_text="email", width=150, on_change=email_onchange) 
    email_row = ft.Row([email_label, email_in], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                       vertical_alignment=ft.CrossAxisAlignment.CENTER, width=260) 

    # second kind of UI for input 
    password_in = ft.TextField(label='Password', hint_text="Enter Password...", width=260, 
                               password=True, can_reveal_password=True, on_change=password_onchance) 
    
    # functions to handle signup/login first, to deal with buttons 
    def show_alert(msg): # easy to code but a bit annoying 
        debug_print("TRYING TO DISPLAY '{}'".format(msg))
        page.open(ft.AlertDialog(title=ft.Text(msg, color=ft.colors.RED))) 
        page.update()

    def disable_buttons(): 
        signup_btn.disabled = True 
        login_btn.disabled = True 
        page.update() 
    
    def enable_buttons(): 
        signup_btn.disabled = False 
        login_btn.disabled = False 
        page.update() 
    
    def handle_signup(e): 
        disable_buttons() # to let it load 
        res = fh.signup_email_password(email_in.value, password_in.value) 
        enable_buttons() # restore normal functionality 

        debug_print("HANDLE SIGNUP RES:", res)
        if isinstance(res, Exception): 
            debug_print("ERROR:", str(res))
            
            # ERRORED! 
            show_alert("Signup failed: {}".format(str(res))) 
        else: 
            # SUCCESS! 
            global current_user 
            current_user = res 
            nextpage() 

    
    def handle_login(e): 
        disable_buttons() # to let it load 
        res = fh.login_email_password(email_in.value, password_in.value) 
        enable_buttons() # restore normal functionality 

        debug_print("HANDLE LOGIN RES:", res)
        if isinstance(res, Exception): 
            debug_print("ERROR:", str(res))
            # ERRORED! 
            if "INVALID_LOGIN_CREDENTIALS" in str(res): 
                show_alert("Invalid login credentials for login") 
            else: 
                show_alert("Login failed: Unknown Error\n\nDetails: {}".format(str(res))) 
            
        else: 
            # SUCCESS! 
            global current_user 
            current_user = res 
            nextpage() 
    
    # buttons 
    signup_btn = ft.ElevatedButton("Sign Up", width=100, on_click=handle_signup, 
                               style=ft.ButtonStyle(side=ft.BorderSide(1, colours.blue.hex), 
                                                    bgcolor=colours.buttonColsFor(colours.white), elevation=1, 
                                                    text_style=ft.TextStyle(color=colours.darkgrey.hex))) 
    login_btn = ft.FilledButton("Login", width=100, on_click=handle_login, 
                             style=ft.ButtonStyle(bgcolor=colours.buttonColsFor(colours.blue), elevation=1, 
                                                   text_style=ft.TextStyle(color=colours.white.hex))) 
    
    buttons = ft.Row([signup_btn, login_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                     vertical_alignment=ft.CrossAxisAlignment.CENTER, width=260) 


    # put it all together to a login tab 
    login_tab = ft.Column([appname_label, email_row, password_in, buttons], spacing=20, alignment=ft.MainAxisAlignment.SPACE_EVENLY, 
                          horizontal_alignment=ft.CrossAxisAlignment.START, width=260, height=300) 
    
    page_container = ft.Container(content=login_tab, 
                                  margin=30, 
                                  width=260, 
                                  alignment=ft.Alignment(0.5, 0.5)) 

    page.add(page_container) 
    
    page.update() 




def dashboard_page(page:ft.Page, pageback, clean_page=True): 
    debug_print("DASHBOARD PAGE")

    if clean_page: 
        page.clean() # in case we're coming from another page, clear the page 

    # logout function 
    def logout(e): 
        global current_user 
        current_user = None # delete it 
        pageback() 
        

    # quick basic UI 
    page.add(ft.Column([ft.Text("YAY LOGGED IN: {}".format(current_user['localId'])),
                        ft.ElevatedButton("Log out", style=ft.ButtonStyle(bgcolor={
                            ft.ControlState.DEFAULT: colours.white.hex, 
                            ft.ControlState.HOVERED: colours.Color(hsv=colours.hex_to_adjusted_hsv(
                                colours.red, [0, -0.35, 0.2])).hex, 
                        }, side=ft.BorderSide(1, color=colours.red.hex), 
                            color=colours.red.hex, elevation=1), on_click=logout)], 
                        spacing=10)) 


    # current_user.localId is a unique ID for each user, can be used in firestore database or other stuff

    
    page.update() 





def app(page:ft.Page): 
    page.title = "Login logout flet demo" 

    page.window.height = 500 
    page.window.width = 320 

    global current_user 
    current_user = None 
    
    def show_login_page(): # funny stuff to make the syntax work 
        login_page(page, lambda:dashboard_page(page, show_login_page)) 
    
    show_login_page() 



ft.app(target=app) 

