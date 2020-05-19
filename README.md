# 19OLEES STORE

This applicatopn is called 19OLEES STORE, which is a web based application. People can visit it and view all products in 19OLEES STORE. The purpose of creating this website is that to help people stay healhty and live better. The 19OLEES STORE is a convinent store located at 190 lEES avenue, ottawa. Because of Covid-19 pandenmic, it is not safe to shopping at a store. By listing all products online, customers could register and order their products online and pick them up outside of store or request a delivery. This method could help customers stay healthy and live better.

This website has admin management system and users login system. For admin management system, administrator has to use default password to login to system. After login, administrator could update default password, add products' catrgories and add product in related category. Administrator could delete each category and update each category's name and picture. It could also delete, update each product's name, price, image and description. For registered users, they could add products to their carts and submit management system. Adminstrator could view it and prepare it.

## A. Prerequisites

### A1. Pyhton version

The 19OLEES STORE application is developed with Pyhton version `3.8.0` and FLASK version `1.1.1`.

### A2. System dependencies

The 19OLEES STORE application has the following system dependencies.

* Postgresql Client Libraries 12.x or newer

## B. Development

### B1. Database creation
`python`
`from application import db`
`db.create_all()`


### B2. How to run this application
Simply execute the following command: `export FLASK_APP=application.py && flask run`