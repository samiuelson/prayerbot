#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import json
from web import db
from dbms.models import Intent
from facebook import utils
from translations.user import user_gettext
from facebook.api import FacebookApi
from events import PrayerEvent
import time

def confirm_praying_for_intention():

    # for debugging
    #print "***********************************\n";
    #print int(time.time())-60*60*24*30
    #print time.ctime( int(time.time()-60*60*24*30 ))
    #print "\n";

    # Delete old intentions - older than 30 days - 60 seconds * 60 minutes * 24 hours * 30 days
    query_prayers = Intent.query.filter(Intent.ts < int(time.time())-60*60*24*30).all();
    for prayer in query_prayers:
        db.session.delete(prayer)

    db.session.commit()
    db.session.flush()


    # Send reminder
    query_prayers = Intent.query.filter( Intent.commiter_id > 0, Intent.confirmed == 0 ).all();

    for prayer in query_prayers:
        if prayer.commiter_id != None and prayer.commiter_id != "":
            options = [ {
                        'title': user_gettext( prayer.commiter_id, u"Yes" ),
                        'payload': PrayerEvent.payload(PrayerEvent.DID_PRAY, prayer.id, prayer.user_id)
                        },
                        {
                        'title': user_gettext( prayer.commiter_id, u"No" ),
                        'payload': PrayerEvent.payload(PrayerEvent.DONT_CONFIRM_PRAY, prayer.id, prayer.user_id)
                    } ]

            response_message = utils.response_buttons(
                user_gettext( prayer.commiter_id, u"Did You pray in below request ?\n%(value)s", value=prayer.description ),
                options
                )

            response = json.dumps({
                        'recipient': { 'id' : prayer.commiter_id },
                                        'message': response_message
                                })

            api = FacebookApi();
            api.post("/me/messages", response);



if __name__ == '__main__':
    confirm_praying_for_intention()


