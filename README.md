# Catalog App

## Installation
Install [Vagrant](http://vagrantup.com/)<br>
Install [VirtualBox](https://www.virtualbox.org/)<br>
Clone [this project](https://github.com/frost-byte/restaurantMenus.git)<br>

1. **Use One of the Following Programs**
    - Git Bash on Windows
    - Terminal on Mac
    - Shell on Linux
&nbsp;
- **Navigate to the vagrant folder in the cloned repository.**
- Type the command **vagrant up**
- Type **vagrant ssh** to connect to the vagrant VM. (see below for setting up SSH on Windows)

Check the section **Using the Vagrant Virtual Machine** [here](https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true) for more information.<br>

## SSH on Windows
If you opt to use cmd.exe in Windows, you will be able to bring up the Vagrant VM.
However, when you try to use "vagrant ssh" you will probably receive a message similar to the following:
```
`ssh` executable not found in any directories in the %PATH% variable. Is an
SSH client installed? Try installing Cygwin, MinGW or Git, all of which
contain an SSH client. Or use your favorite SSH client with the following
authentication information shown below:

Host: 127.0.0.1
Port: 2222
Username: vagrant
Private key: C:/Path/to/catalog/vagrant/.vagrant/machines/default/virtualbox/private_key
```
If you are running Windows, then the ```private_key.ppk``` included in this same directory can be used in PuTTY to ssh into the Vagrant/VirtualBox VM.

Follow the guide under the [References SSH](#SSH) section.
The following configuration should be setup in PuTTY:<br>

####Session
**Host Name**:  ```127.0.0.1``` or ```localhost```

####Connection -> Data
**Auto-login username**: ```vagrant```

####Connection -> SSH -> Auth
**Private key file for authentication**: Browse to the .ppk file in

Once you've specified the above, go back to **Session** and under **Saved Sessions** enter a name for your config and click the "Save" button to the right of the list of Saved Sessions.

From this point on all you'll have to do to start the session is open PuTTY and double click on your config in the Saved Sessions list.

## The Database
From your ssh terminal, navigate to the project's root directory.

```cd /vagrant/catalog```

Run the script to populate the Database.

```python catalog/populator.py -r```

## Google OAuth2 API
Refer to  the instructions [Here](https://support.google.com/cloud/answer/6158849?hl=en&ref_topic=6262490) to setup OAuth2.

Open the [Google Developer's Console](https://console.developers.google.com/) and
perform the following steps.


####Consent Screen
1. Set __Product name shown to users__ to __CatalogApp__
2. Click __Save__.

####Credentials
1. Under the __API Manager__, Select __Credentials__ in the Sidebar.
+ Select the __Credentials tab__ in the main view.<br>
+ Click on the __Add credentials__ dropdown button.
+ Specify __OAuth 2.0 client ID__
+ For **Application Type** select the __Web application__ radio button
+ Enter __Catalog App__ in the __Name__ field.
+ In the __Authorized redirect URIs__ field enter http://localhost:5000/gconnect<br>
+ Click __Save__ to store the credentials
+ Then click the **Download JSON** button.
+ Save the __client_secret.json__ file to the project's root directory: **/vagrant/catalog**


####Google APIs
1. Under the __API Manager__ in the [Google Developer's Console](https://console.developers.google.com/), click __Overview__ in the sidebar.
+ Click the __Google APIs__ tab in the main view.
+ Under __Social APIs__ select __Google+ API__
+ If not already enabled, click the __Enable API__ button


## Server
From the project's root directory - __/vagrant/catalog__<br>
```python runserver.py```

Open a browser page to ```localhost:5000```

#### Endpoints
The following api endpoints have been provided for the Catalog app.

__JSON__<br>
     [localhost:5000/catalog/JSON](localhost:5000/catalog/XML)<br>

__XML__<br>
[localhost:5000/catalog/XML](localhost:5000/catalog/XML)


#### The Catalog APP
Without logging in, you should be able to only view records, these include:
1. All __Items__.
+ __Items__ in each __Category__.

After logging into the app using Google+ you should be able to do the following:

1. Add new Items to a Category.
2. Edit Items that you have created.
3. Delete Items that you have created.

The Add and Edit forms allow you to upload an image for an Item.

## Requirements
+ Vagrant VM
+ VirtualBox
+ Clone of this Repository

## Libraries
+ [dicttoxml](https://pypi.python.org/pypi/dicttoxml)

##References

###Code Formatting
[Pep8 Online](http://pep8online.com/)<br>
An online python formatting tester.

[Flake8](https://flake8.readthedocs.org/en/2.4.1/)<br>
A Handy, command line tool for checking the formatting of your python code.

###Code Attributions


###Other API and Coding References
[Stack Overflow](http://stackoverflow.com/)<br>
A go to resource for solving all problems related to coding.

[W3Schools](http://www.w3schools.com/)<br>
Great reference for all languages and specifications for programming web based content. HTML, CSS, jQuery, Javascript...


###SSH
[How To Use SSH Keys with PuTTY and PuTTYGen](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-putty-on-digitalocean-droplets-windows-users)<br>
[PuTTY for Windows](http://www.chiark.greenend.org.uk/~sgtatham/putty/)<br>

