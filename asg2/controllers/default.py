# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    listings = db().select(db.listings.ALL)
    return dict(listings=listings)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def show():
    listing_id = request.args[0]
    listing = db(db.listings.id==listing_id).select().first()
    images = db(db.images.listing_id==listing_id).select()
    return dict(listing=listing, images=images)

def upvote():
    seller_id = request.args[0]
    row = db(db.sellers.id==seller_id).select().first()
    row.upvotes = row.upvotes + 1
    row.update_record()
    row.rating = row.upvotes - row.downvotes
    row.update_record()
    return row.rating

def downvote():
    seller_id = request.args[0]
    row = db(db.sellers.id==seller_id).select().first()
    row.upvotes = row.upvotes - 1
    row.update_record()
    row.rating = row.upvotes - row.downvotes
    row.update_record()
    return row.rating

@auth.requires_login()
def add():
    form = SQLFORM.factory(db.sellers, db.listings)
    if form.process().accepted:
        id = db.sellers.insert(**db.sellers._filter_fields(form.vars))
        form.vars.seller=id
        id = db.listings.insert(**db.listings._filter_fields(form.vars))
        form.vars.listing_id=id
        listing_id = form.vars.listing_id
        redirect(URL('upload', args=[listing_id]))
    return dict(form=form)

def upload():
    form = SQLFORM(db.images)
    form.vars.listing_id = request.args[0]
    if form.process().accepted:
        redirect(URL('upload', args=request.args[0]))
    return dict(form=form)
