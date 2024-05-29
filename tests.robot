*** Settings ***
Documentation     A test suite for the login functionality of the practice test automation website.
Library           SeleniumLibrary
#Library           ChatGptAssistant.py   verbose=True
Library           OperatingSystem


*** Variables ***
${BROWSER}        Headless Chrome
${URL}            https://practicetestautomation.com/practice-test-login/
${USERNAME}       student
${PASSWORD}       Password123
${SUCCESS_URL}    https://practicetestautomation.com/logged-in-successfully/

*** Keywords ***
Test Teardown
    Run Keyword If Test Failed   Log    MESSAGE FROM TEARDOWN IN CASE OF FAILING TEST
    ${page}=  Get Source
    Set Global Variable    ${PAGE_SOURCE}    ${page}
    Close Browser

AI Setup
    [Tags]   openbrowser
   # Prepare Assistant    roboAssistant
    Open Browser    ${URL}    ${BROWSER}

AI Teardown
    Run Keyword If Test Failed   Log    MESSAGE FROM TEARDOWN IN CASE OF FAILING TEST
    Delete Assistant
    ${page}=  Get Source
    Set Global Variable    ${PAGE_SOURCE}    ${page}
    Close Browser

*** Test Cases ***
Test assistant usage
    [Setup]        Prepare Assistant    roboAssistant
    [Teardown]     Delete Assistant
    [tags]         prepare
    Ask Question From Assistant    On what country is Rovaniemi?
    Ask Question From Assistant    What is the capital of that country?
    Ask Question From Assistant    What is the population of that capital?


Valid Login Test
    [Documentation]    Tests a valid login scenario.
    [Setup]       Open Browser    ${URL}    ${BROWSER}    options=binary_location="/usr/local/bin/chrome"
    [Teardown]    Test Teardown
    [Tags]    passing
    Wait Until Page Contains Element    id:username    10s
    Input Text    //input[@id='username']    ${username}
    Input Text    //input[@id='password']    ${password}
    Click Button    id:submit
    Wait Until Page Contains    Logged In Successfully    10s
    ${current_url}=    Get Location
    Should Be Equal As Strings    ${current_url}    ${SUCCESS_URL}

Describe Web Page
    [Documentation]    Tests a valid login scenario.
    [Setup]       AI Setup
    [Teardown]    AI Teardown
    [Tags]    assistant
    Wait Until Page Contains Element    id:username    10s
    ${page_source}=   Get Source
    Create File    ${OUTPUT DIR}/page.html    ${page_source}
    Add File To Assistant    testpage       ${OUTPUT DIR}/page.html
    Ask Question From Assistant   using given page.html file, please describe the web page on it. please be extra verbose.

Describe Valid Hidden Content Test
    [Documentation]    Tests a valid login scenario.
    [Setup]       AI Setup
    [Teardown]    AI Teardown
    [Tags]    hidden
    Wait Until Page Contains Element    id:username    10s
    Input Text    //input[@id='username']    ${username}
    Input Text    //input[@id='password']    ${password}
    Click Button    id:submit
    Wait Until Page Contains    Logged In Successfully    10s
    ${current_url}=    Get Location
    Should Be Equal As Strings    ${current_url}    ${SUCCESS_URL}
    ${page_source}=   Get Source
    Create File    ${OUTPUT DIR}/hiddenpage.html    ${page_source}
    Add File To Assistant    hiddenpage       ${OUTPUT DIR}/hiddenpage.html
    Ask Question From Assistant   use given hiddenpage.html file. Give only textual listing of links and link urls found from hiddenpage file


Get Button Xpath Locator
    [Documentation]    Tests a valid login scenario.
    [Setup]       AI Setup
    [Teardown]    AI Teardown
    [Tags]    xpath
    Wait Until Page Contains Element    id:username    10s
    ${page_source}=   Get Source
    Create File    ${OUTPUT DIR}/page.html    ${page_source}
    Add File To Assistant    testpage       ${OUTPUT DIR}/page.html
    Ask Question From Assistant   using given page.html file, please tell me the xpath for username field

Invalid Login Test
    [Documentation]    Tests a valid login scenario.
    [Setup]       Open Browser    ${URL}    ${BROWSER}
    [Teardown]    Test Teardown
    [Tags]    failing
    Wait Until Page Contains Element    id:username    10s
    Input Text    //input[@id='username']    ${username}
    Input Text    //iput[@id='password']    ${password}
    Click Button    id:submit
    Wait Until Page Contains    Logged In Successfully    10s
    ${current_url}=    Get Location
    Should Be Equal As Strings    ${current_url}    ${SUCCESS_URL}


Playwright Python
    [Documentation]    Tests a valid login scenario.
    [Setup]          Run Keywords      AI Setup      AND      Prepare Assistant    roboAssistant      you reply back in Playwright + Python code only. The documentation for it is here https://playwright.dev/python/docs/intro use it as basis for the reply
    [Teardown]    AI Teardown
    [Tags]    playwrightpy
    Wait Until Page Contains Element    id:username    10s
    ${page_source}=   Get Source
    Create File    ${OUTPUT DIR}/page.html    ${page_source}
    Add File To Assistant    testpage       ${OUTPUT DIR}/page.html
    Ask Question From Assistant   using given page.html file, please generate at least 3 test cases for this page. On the page there are id's for each element to use in for example login procedure, use only the ones you see on the page html. Use only the locators you see in the html page, do not make up any id's that I should replace but put the correct ones in place. in case of no id's use xpaths

Figma File Test Plan
    [Documentation]    Tests a valid login scenario.
    [Setup]        Prepare Assistant    roboAssistant      you reply in Robot Framework's AppiumLibrary code and test steps listed as plain text
    # [Teardown]    AI Teardown
    [Tags]    figmafile
    # Wait Until Page Contains Element    id:username    10s
    # ${page_source}=   Get Source
    # Create File    ${OUTPUT DIR}/page.html    ${page_source}
    Add File To Assistant    testpage       ${OUTPUT DIR}/figmasample.pdf
    Ask Question From Assistant   using given figmasample.pdf file, please describe what the application is for. What does it do? Generate at least 3 test cases for the mobile app it represents, login not included in the tests. Use only List the test steps and also generate RobotFramework test script using AppiumLibrary for Robot Framework
