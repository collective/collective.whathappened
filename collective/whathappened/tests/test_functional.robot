*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Create folder and content, subscribe to folder, check subscribe and notifications
    Given I'm logged in as the site owner

     When I add a folder 'My folder'
      And I add and publish a document 'Test document' in 'my-folder'
      And I subscribe to 'my-folder'
      And I rename the content's title of 'test-document' in 'my-folder' to 'New document title'
      And I go to 'my-folder/test-document'

     Then The subscribe button should not be visible
#      And There should be a hot notifications 'admin has renamed /plone/test-document'


*** Keywords ***

My Rename Content Title
    [arguments]  ${folder}  ${id}  ${new_title}

    Go to  ${PLONE_URL}/${folder}/${id}/object_rename
    Input Text for sure  css=input#${id}_title  ${new_title}
    Click Button  Rename All
    Go to  ${PLONE_URL}/${folder}/${id}

I'm logged in as the site owner
    Log in as site owner
    Go to homepage

I subscribe to '${path}'
    Go to  ${PLONE_URL}/${path}/@@collective_whathappened_subscribe_subscribe

I go to '${path}'
    Go to  ${PLONE_URL}/${path}

I add a folder '${folder}'
    Add folder    ${folder}

I add and publish a document '${document}' in '${folder}'
    Go to  ${PLONE_URL}/${folder}
    Open add new menu
    Click link  id=document
    Wait Until Page Contains Element  css=#archetypes-fieldname-title input
    Input Text  title  ${document}
    Click Button  Save
    Page should contain  ${document}
    Element should contain  css=#parent-fieldname-title  ${document}
    Workflow Publish

I rename the content's title of '${content}' in '${folder}' to '${title}'
    My Rename Content Title    ${folder}  ${content}  ${title}

I remove the content '${content}'
    Remove Content    ${content}

The subscribe button should not be visible
    Element should not be visible  css=.subscribe

There should be a hot notifications '${notification}'
    Element should contain  css=#personaltools-notification a  ${notification}