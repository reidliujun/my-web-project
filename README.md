# Project plan

> *General description of what you are doing and how you are doing that (what kinds of views, models are needed), how they relate to each other, and what is the implementation order and timetable.*

> - *What features you plan to implement?*

> - *Are there some extra features not listed in the project description what you plan to implement?*

> - *For each feature, how do you plan to implement it?*

## Graded Items

**Authentication (mandatory, 100-200 points)**

Database establishment in Django (django.auth). Functions including login, logout and register. User can edit and view with authentication. User authentication includes username and password.

**Basic album functionalities (mandatory, 250-500 points)**

Multi album, edit albums and photos, for example, add and remove. Layout selection for the album page. Using Django framework, models design attached in the last page.

Function details: dragging photo to the album page layout from the photo pool.

**Public link to photo albums (max 70 points)**

Provide a public link just like google doc. Not allow editing.

Possible way: saved the album in database with a random key value (probably hash and key generated according to the time stamp and album name). The public link could be “url + key”.

**Share albums (max 80 points)**

Publish the generated public link to Facebook. (use [facebook share javascript api for web](https://developers.facebook.com/docs/plugins/share-button/)

**Order albums (mandatory, 50-200 points)**

Order page: copy number, address, price calculate and order to go to the payment page.

Payment page: Generate pid, sid and amount, return success_url, cancel_url and error_url. Checksum process included.

**Integrate with an image service API (max 100 points)**

Two ways of adding photo to the pool:

1. add photo (possibly entire dir) from the photo server (personal photos)

2. add photo by searching in flickr (possibile gallery api: using the personal flickr photo pool with the user ID ).

**3rd party login (max 100 points)**

Facebook. Use [Facebook login api for javascript](https://developers.facebook.com/docs/facebook-login/login-flow-for-web/)

**Use of Ajax (max 100 points)**

Operation like page flipping, dragging and dropping saved in server.

## Models *( -> User, Album, Order, Page, Photo)*

### User (from django.contrib.auth)

**username**

As per docs: “Required. 30 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters.”

**password**

As per docs: “Required. A hash of, and metadata about, the password. (Django doesn’t store the raw password.) Raw passwords can be arbitrarily long and can contain any character.”

### Album

**title: CharField**

An album can be given a title.

**public_url_suffix: string**

The string that needs to be appended to our website url to gain read access to album without login. Generated for the user upon request.

**collaboration_url_suffix: string**

The string that needs to be appended to url to gain write access to album. Generated upon the album owner’s request.

**User: ManyToMany**

One user can create/own multiple albums. An album can have more than one owner, should users want to collaborate. Once a user gives ownership to another user, both are able to view, edit, delete, or purchase the album. This might perhaps be done either by the current owner inviting the to-be owner by typing out their user name, or by sending a single use gain-ownership link.

### Order

**User: ForeignKey**

An order belongs to a single user, the one who made the purchase. One user can make multiple purchases.

**name: CharField**

For delivery. Required.

**street_address: CharField**

For delivery. Required.

**post_code_and_city: CharField**

For delivery. Grouped together due to regional differences in format. F.ex. “XXXXX City” in Finland, “City, State, XXXXX” in USA, etc. Required.

**country: CharField**

For delivery. Required.

**order_time: DateTimeField**

Date on which the order was made. For quality control.

**shipping_time: DateTimeField**

Date on which the product was shipped. For quality control.

### Page

**Album: ForeignKey**

An album can have many pages, each page unique to that album.

**layout: PositiveSmallIntegerField**

A page can have various layouts with regards to placement and size of photos.

### Photo

**Album: ManyToMany**

Users can add photos into an album’s photo pool. This pool of photos will be displayed to the user while they create/edit their album, to allow them to see the photos they have available when making layout choices. A particular photo can also belong to the photo pool of other albums.

**Page: ManyToMany**

A photo can exist on many different pages and different pages can contain the same photo.

## Urls / Views

The app will consist of four separate pages (login, album selection, album browse/edit, order).

- *app.host.tld/$* will lead to the album selection view (unless not logged in, in which case to the login page).

- *app.host.tld/album_id/$* will lead to album browse page (unless not logged in as owner of album, in which case back the album selection page with an error if logged in, to login page otherwise).

- *app.host.tld/album_id/edit$* will lead to album edit page (unless not logged in as owner of album, in which case back the album selection page with an error if logged in, to login page otherwise).

- *app.host.tld/order_id/$* will lead to the order page (unless not logged in as user who made the order).

- *app.host.tld/order_id/.{20}$* will check string for the collaboration or share strings, if it matches, do the required action (add user as album owner or just show album in browse mode), otherwise to the login screen with an error


## Implementation Order (now: dec 13, week 50; due: feb 14, week 7)

1. Database/models functionality. (weeks 51 - 2)

2. Views. (weeks 51 - 3)

3. Basic UI functionality (album browsing, album editing). (week 51 - 3)

4. Authentication. (week 2)

5. UI honing. (week 2)

6. Public link generation. (week 2 - 3)

7. Share on third party service. (week 2 - 3)

8. Ordering function. (week 3)

9. Third party photo import. (week 4)

10. Third party login. (week 4)

11. Testing/tweaking. (week 5)


Will maybe add pictures/mockups. We have some. :)

