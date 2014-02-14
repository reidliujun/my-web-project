<hr><hr>

![Fotosynteesi Logo](Fotosynteesi/website/static/images/logo_full.gif?raw=true)

<hr><hr>


> *General description of what you are doing and how you are doing that (what kinds of views, models are needed), how they relate to each other, and what is the implementation order and timetable.*

> - *What features you plan to implement?*

> - *Are there some extra features not listed in the project description what you plan to implement?*

> - *For each feature, how do you plan to implement it?*


###Statement: I (Jun Liu) agree this project to be forked on 14.02.2014 17:34 by Erik Enomaa.

<hr><hr>
# Final submission infomation
###Your names and student-ids:
Name: Jun Liu

Student ID: 275194 

###What features you implemented and how much points you would like to give to yourself from those? Where do you feel that you were successful and where you had most problems.

We have implemented user system, album public link generation, public share, social login and album share, album order, ajax using, photo upload with given url and elements delete (include album, page and images delete).

I think the ajax detection of conflict album title and image drag feature are successful and the problems include database design, website UI design and url design.

###How you divided the work between the team members - who did what?

I  (Jun Liu) have done the following jobs:

-facebook login and share

-part of the models design (order model part) 

-UI design 

-javascript including ajax and images drag and delete 

-80%-90% views code (included the ajax and post request handle, redirect) and all order feature.

-all the templates creation 

-URL design

Erik has done the following jobs:

Project plan -> full credit.

Models -> plan and execution except order part

Views -> login related views.

###Instructions how to use your application and link to Heroku where it is deployed.

1. Once visit our website, first user can register and login as a user, and user can also login use facebook account, it will redirect to the page after facebook authorized.
2. User can create album, pages. When user creates album by adding the title, ajax will detect whether this title is available or not when the mouse not focus in the input area. When user create the page, he can choose the layout and drag the photos from the images pool to the page, and it will directly append the photos to the pages. Also, user can drag the photos back to the gallery and this will detached the images to the special page.
3. User can add photo after choose the layout style, and user can also add and view the photo by clicking the "photo" tag in the navigation bar
4. User can also share, order and delete the album when in the “/album” page. 
5. User can view all the the order history and account information by clicking the username in the navigation bar.

###The link to heroku: fotomemo.herokuapp.com




# General information about the project
This project is intended to be run on Python 2.7.2, with other dependencies as noted in requirements.txt.




# Requirements / Graded Items

###Valid CSS and HTML
"(use a validator... we will)"

###Should work on modern browsers
"especially Firefox or Chrome which conform to standards rather well"

###Code should be commented well enough
***Seriously.***

###Avoiding excessive use of third-party libraries for graded features
"Although in real life you might use an existing django app for some parts of your project, beware of “externalizing” all aspects of the project. We will only grade the part you wrote."

###Authentication (mandatory, 100-200 points)
Database establishment in Django (django.auth). Functions including login, logout and register. User can edit and view with authentication. User authentication includes username and password.

###Basic album functionalities (mandatory, 250-500 points)
Multi album, edit albums and photos, for example, add and remove. Layout selection for the album page. Using Django framework, models design attached in the last page.
Function details: dragging photo to the album page layout from the photo pool.

###Public link to photo albums (max 70 points)
Provide a public link just like google doc. Not allow editing.
Possible way: saved the album in database with a random key value (probably hash and key generated according to the time stamp and album name). The public link could be “url + key”.
Comments: in this version, the url is a hexdigest generated using username and album title.

###Share albums (max 80 points)
Publish the generated public link to Facebook (using [facebook share javascript api for web](https://developers.facebook.com/docs/plugins/share-button/)).

###Order albums (mandatory, 50-200 points)
Order page: copy number, address, price calculate and order to go to the payment page.
Payment page: Generate pid, sid and amount, return success_url, cancel_url and error_url. Checksum process included.

###Integrate with an image service API (max 100 points)
Two ways of adding photo to the pool:
1. add photo (possibly entire dir) from the photo server (personal photos)
*Note: This has to at least be able to add by url! Upload functionality is secondary.*
2. add photo by searching in flickr (possibile gallery api: using the personal flickr photo pool with the user ID ).

###3rd party login (max 100 points)
Facebook. Use django-facebook app for easy use (https://github.com/tschellenbach/Django-facebook)

###Use of Ajax (max 100 points)
Album title conflicts detection, images dragging and dropping saved in server.

###Non-functional requirements (max 200 points)
Overall **documentation**, demo **(\*)**, teamwork, and project management as seen from the history of your github project.

**(\*)** *Note: The execution for this should be planned (30 min in duration).*

<hr><hr>
# Models
*( -> User, Album, Order, Page, Photo)*

## User (from django.contrib.auth)

###username
As per docs: “Required. 30 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters.”

###password
As per docs: “Required. A hash of, and metadata about, the password. (Django doesn’t store the raw password.) Raw passwords can be arbitrarily long and can contain any character.”

## Album

###title: CharField
An album has to be given a title. Unique to a user.

###public_url_suffix: string
The string that needs to be **appended** to **our website url** to gain read access to album without login. Generated for the user **upon request**.

###collaboration_url_suffix: string
The string that needs to be **appended** to url to gain write access to album. Generated **upon** the album owner’s **request**.

###User: ManyToMany
One user can create/own multiple albums. An **album can have more than one owner**, should users want to collaborate. Once a user gives ownership to another user, both are able to view, edit, delete, or purchase the album. This might perhaps be done either by the current owner inviting the to-be owner by typing out their user name, or by sending a single use gain-ownership link.

##Order

###User: ForeignKey
An order belongs to a single user, the one who made the purchase. One user can make multiple purchases.

###name: CharField
For delivery. Required.

###street_address: CharField
For delivery. Required.

###post_code_and_city: CharField
For delivery. Grouped together due to regional differences in format. F.ex. “XXXXX City” in Finland, “City, State, XXXXX” in USA, etc. Required.

###country: CharField
For delivery. Required.

###order_time: DateTimeField
Date on which the order was made. For quality control.

###shipping_time: DateTimeField
Date on which the product was shipped. For quality control.

## Page

###Album: ForeignKey
An album can have many pages, each page unique to that album.

###layout: PositiveSmallIntegerField
A page can have various layouts with regards to placement and size of photos.

## Photo

###Album: ManyToMany
Users can add photos into an *album’s* **photo pool**. This pool of photos will be **displayed to the user while they create/edit their album**, to allow them to see the photos they have available when making layout choices. A particular photo can also belong to the photo pool of other albums.

**TODO:** *Let's discuss what's best to do here. However, I feel pretty strongly about photos **not** living inside page objects. Deleting a page should only 'unlink' the photo from the page, nothing more.*

###Page: ManyToMany
A photo can exist on many different pages and different pages can contain the same photo.

*Note:* **Adding a photo** *from an album's photo pool* **to a page, should**, *however*, **remove it** *from that pool. Otherwise it will be a major inconvenience for the user to keep track of which photos they have already used.*

<hr><hr>
# Urls / Views
The app will consist of four separate pages (login, album selection, album browse/edit, order). All urls (except register, about) will redirect to login, if not already logged in.

URL | Action / View
--- | ------
*app.host.tld/$*                | will redirect to '/u/\<username\>/a/'
*app.host.tld/u/\<username\>/a/$* | leads to the album selection view.
*app.host.tld/u/\<username\>/$*   | leads to user information/settings.
*app.host.tld/u/*               | redirects to '/u/\<username\>/'
*app.host.tld/u/\<username\>/a/\<album_title\>/$* | will lead to album browse/edit page (unless not logged in as owner/collaborator of album, in which case back the album selection page with an error).
*app.host.tld/u/\<username\>/o/$* | will lead to the user's complete order history page.
*app.host.tld/u/\<username\>/o/\<order_id\>/$* | will lead to the information page of the specific order
*app.host.tld/u/\<username\>/a/\<albumtitle\>/.{20}$* **(\**)** | will check string for the album's collaboration **(\*)** or share strings, if it matches, do the required action (add user as album owner or allow to browse as guest)
*app.host.tld/register/$* | leads to registration page

**(\*)** *Note: Collaboration url should take the guest to the login/registration page, because it seems more sensible to not let guests collaborate (no safety in that, since can't sign out, etc.).*

**(\**)** *Note: '\<username\>' in this case refers to the user name of the album creator, edit rights are stored in the model (and are viewable/revokable (revokable only by creator) from (* **TODO:** *both or either?) from user settings and/or album settings).*

## Implications:

- Usernames can serve as user IDs.

- Album titles are unique for any one user, **not globally**.

*Note: This is important, because we cannot have it so that '/album/\<album_title\>/'
is the album url and as a result only one user can have an album called "Florida Trip"*



<hr><hr>
# Mockups
![Album View](Fotosynteesi/readme_files/album_view.jpg?raw=true)
![Page View](Fotosynteesi/readme_files/page_view.jpg?raw=true)
![Layout Selection View](Fotosynteesi/readme_files/layout_selection.jpg?raw=true)

<hr><hr>
# Implementation Order
*(now: feb 10, week 7; due: feb 14, week 7 - **4 days remaining** )*

1. Database/models functionality. (week 5)
2. Views. (week 5 - 6)
3. Public link generation. (week 5 - 6)
4. Ordering function. (week 5- 6)
5. Third party photo import. (week 5 - 6)
6. Basic UI functionality (album browsing, album editing). (week 7)
7. Authentication. (week 7, mostly done as is)
8. Third party login. (status of this?)
9. UI honing. (week 7)
10. Share on third party service. (week 7)
11. Testing/tweaking. (week 7)


<hr><hr>
