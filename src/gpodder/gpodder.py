#!/usr/bin/env python
# -*- coding: UTF8 -*-

# Python module src/gpodder/gpodder.py
# Autogenerated from gpodder.glade
# Generated on Tue Nov 22 14:11:54 2005

# Warning: Do not modify any context comment such as #--
# They are required to keep user's code

#
# gPodder
# Copyright (c) 2005 Thomas Perl <thp@perli.net>
# Released under the GNU General Public License (GPL)
#

import os
import gtk
import gobject
import sys
from threading import Event


from SimpleGladeApp import SimpleGladeApp
from SimpleGladeApp import bindtextdomain

from libpodcasts import podcastChannel
from libpodcasts import podcastItem

from libpodcasts import channelsToModel

from librssreader import rssReader
from libwget import downloadThread

from libgpodder import gPodderLib
from libgpodder import gPodderChannelReader
from libgpodder import gPodderChannelWriter

# for isDebugging:
import libgpodder

app_name = "gpodder"
app_version = "unknown" # will be set in main() call
app_authors = [ "Thomas Perl <thp@perli.net>" ]
app_copyright = "Copyright (c) 2005 Thomas Perl"
app_website = "http://www.perli.net/projekte/gpodder/"

#glade_dir = "../data"
glade_dir = "/usr/share/gpodder/"
icon_dir = "/usr/share/gpodder/images/gpodder.png"
locale_dir = ""

bindtextdomain(app_name, locale_dir)


class Gpodder(SimpleGladeApp):
    channels = []
    
    active_item = None
    items_model = None
    
    active_channel = None
    channels_model = None

    channels_loaded = False

    def __init__(self, path="gpodder.glade",
                 root="gPodder",
                 domain=app_name, **kwargs):
        path = os.path.join(glade_dir, path)
        SimpleGladeApp.__init__(self, path, root, domain, **kwargs)

    #-- Gpodder.new {
    def new(self):
        if libgpodder.isDebugging():
            print "A new %s has been created" % self.__class__.__name__
        #self.gPodder.set_title( self.gPodder.get_title())
        #self.statusLabel.set_text( "Welcome to gPodder! Suggestions? Mail to: thp@perli.net")
        # set up the rendering of the comboAvailable combobox
        cellrenderer = gtk.CellRendererText()
        self.comboAvailable.pack_start( cellrenderer, True)
        self.comboAvailable.add_attribute( cellrenderer, 'text', 1)

        # set up the rendering of the treeAvailable treeview
        itemcolumns = [
          #gtk.TreeViewColumn( "", gtk.CellRendererToggle(), active=3),
          gtk.TreeViewColumn( "Episode", gtk.CellRendererText(), text=1),
          gtk.TreeViewColumn( "Size", gtk.CellRendererText(), text=2)
        ]
        
        for itemcolumn in itemcolumns:
            self.treeAvailable.append_column( itemcolumn)

        # xml test
        #reader = rssReader()
        #reader.parseXML( "http://www.perli.net", "test.xml")
        #self.channels.append( reader.channel)
        #reader.parseXML( "http://www.lugradio.org/episodes.rss", "episodes.rss")
        #self.channels.append( reader.channel)
        reader = gPodderChannelReader()
        self.channels = reader.read( False)
        self.channels_loaded = True
        
        # update view
        self.updateComboBox()
    #-- Gpodder.new }

    #-- Gpodder custom methods {
    #   Write your own methods here
    def updateComboBox( self):
        self.channels_model = channelsToModel( self.channels)
        
        self.comboAvailable.set_model( self.channels_model)
        try:
            self.comboAvailable.set_active( 0)
        except:
            print "probably no channels found"
        #self.updateTreeView()
    
    def updateTreeView( self):
        try:
                       self.items_model = self.channels[self.active_channel].getItemsModel()
                       self.treeAvailable.set_model( self.items_model)
        except:
            dlg = gtk.MessageDialog( self.gPodder, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
            dlg.set_markup( "<big>No Channels found</big>\n\nClick on \"Channels\"->\"Add channel..\" to add a new channel.")
            dlg.run()
            dlg.destroy()
            print "probably no feeds or channels found"
    
    def not_implemented( self, message = "some unknown function"):
        dlg = gtk.MessageDialog( self.gPodder, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
        dlg.set_title( "Release early, release often!")
        dlg.set_markup( "<big>Woohoo! You've found a secret..</big>\n\nSorry, but due to the fact that this is just a pre-release, the lazy programmer has just forgotten to implement\n\n<b>" + message + "</b>\n\nHe promises he will in the next release!")

        dlg.run()
        dlg.destroy()

    def set_icon(self):
        icon = self.get_icon('gpodder')
        self.main_widget.set_icon(icon)

    def get_icon(self, entry, size=24):
        #path = self.custom_handler.getIconPath(entry, size)
        path = '/usr/share/gpodder/images/gpodder.png'
        if path == None:
            pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, size, size)
            pb.fill(0x00000000)
        else:
            try:
                pb = gtk.gdk.pixbuf_new_from_file_at_size(path, size, size)
            except:
                pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, size, size)
                pb.fill(0x00000000)
        return pb
    #-- Gpodder custom methods }

    #-- Gpodder.close_gpodder {
    def close_gpodder(self, widget, *args):
        if libgpodder.isDebugging():
            print "close_gpodder called with self.%s" % widget.get_name()
        
        if self.channels_loaded:
            gPodderChannelWriter().write( self.channels)

        self.gtk_main_quit()
    #-- Gpodder.close_gpodder }

    #-- Gpodder.on_itemUpdate_activate {
    def on_itemUpdate_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemUpdate_activate called with self.%s" % widget.get_name()
        reader = gPodderChannelReader()
        #self.channels = reader.read( True)
        #self.labelStatus.set_text( "Updating feed cache...")
        please_wait = gtk.MessageDialog()
        please_wait.set_markup( "<big><b>Updating feed cache</b></big>\n\nPlease wait while gPodder is\nupdating the feed cache...")
        please_wait.show()
        self.channels = reader.read( True)
        please_wait.destroy()
        #self.labelStatus.set_text( "")
        self.updateComboBox()
    #-- Gpodder.on_itemUpdate_activate }

    #-- Gpodder.on_itemPreferences_activate {
    def on_itemPreferences_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemPreferences_activate called with self.%s" % widget.get_name()
        self.not_implemented( "the preferences dialog")
    #-- Gpodder.on_itemPreferences_activate }

    #-- Gpodder.on_itemAddChannel_activate {
    def on_itemAddChannel_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemAddChannel_activate called with self.%s" % widget.get_name()
        result = Gpodderchannel().requestURL()
        if result != None and result != "" and (result[:4] == "http" or result[:3] == "ftp"):
            if libgpodder.isDebugging():
                print "will ADD: " + result
            self.statusLabel.set_text( "Fetching channel index...")
            channel_new = podcastChannel( result)
            channel_new.shortname = "__unknown__"
            self.channels.append( channel_new)
            
            # fetch metadata for that channel
            gPodderChannelWriter().write( self.channels)
            self.channels = gPodderChannelReader().read( False)
            
            # fetch feed for that channel
            gPodderChannelWriter().write( self.channels)
            self.channels = gPodderChannelReader().read( False)
            
            self.updateComboBox()
            self.statusLabel.set_text( "")
    #-- Gpodder.on_itemAddChannel_activate }

    #-- Gpodder.on_itemEditChannel_activate {
    def on_itemEditChannel_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemEditChannel_activate called with self.%s" % widget.get_name()
        self.not_implemented( "the edit channel dialog")
        #print self.channels[self.active_channel].title
    #-- Gpodder.on_itemEditChannel_activate }

    #-- Gpodder.on_itemRemoveChannel_activate {
    def on_itemRemoveChannel_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemRemoveChannel_activate called with self.%s" % widget.get_name()
        try:
            self.channels.remove( self.channels[self.active_channel])
            gPodderChannelWriter().write( self.channels)
            self.channels = gPodderChannelReader().read( False)
            self.updateComboBox()
        except:
            print "could not delete - nothing selected, probably"
    #-- Gpodder.on_itemRemoveChannel_activate }

    #-- Gpodder.on_itemExportChannels_activate {
    def on_itemExportChannels_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemExportChannels_activate called with self.%s" % widget.get_name()
        self.not_implemented( "the export feature")
    #-- Gpodder.on_itemExportChannels_activate }

    #-- Gpodder.on_itemAbout_activate {
    def on_itemAbout_activate(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_itemAbout_activate called with self.%s" % widget.get_name()
        dlg = gtk.AboutDialog()
        dlg.set_name( app_name)
        dlg.set_version( app_version)
        dlg.set_authors( app_authors)
        dlg.set_copyright( app_copyright)
        dlg.set_website( app_website)
        #FIXME: add hanlding hiere dlg.set_logo( gtk.gdk.pixbuf_new_from_file_at_size( "gpodder.png", 164, 164))
        dlg.run()
    #-- Gpodder.on_itemAbout_activate }

    #-- Gpodder.on_comboAvailable_changed {
    def on_comboAvailable_changed(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_comboAvailable_changed called with self.%s" % widget.get_name()
        self.active_channel = self.comboAvailable.get_active()
        self.updateTreeView()
    #-- Gpodder.on_comboAvailable_changed }

    #-- Gpodder.on_treeAvailable_row_activated {
    def on_treeAvailable_row_activated(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_treeAvailable_row_activated called with self.%s" % widget.get_name()
        selection_tuple = self.treeAvailable.get_selection().get_selected()
        selection_iter = selection_tuple[1]
        url = self.items_model.get_value( selection_iter, 0)

        self.active_item = self.channels[self.active_channel].getActiveByUrl( url)
        
        status = Gpodderstatus()
        current_channel = self.channels[self.active_channel]
        current_podcast = current_channel.items[self.active_item]
        if status.setup( current_channel, current_podcast):
            status.download()
        else:
            message_dialog = gtk.MessageDialog( self.gPodder, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
            message_dialog.set_markup( "<big><b>Already downloaded</b></big>\n\nYou have already downloaded this episode.")
            message_dialog.run()
            message_dialog.destroy()
    #-- Gpodder.on_treeAvailable_row_activated }

    #-- Gpodder.on_btnDownload_clicked {
    def on_btnDownload_clicked(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_btnDownload_clicked called with self.%s" % widget.get_name()
        self.on_treeAvailable_row_activated( widget, args)
    #-- Gpodder.on_btnDownload_clicked }


class Gpodderstatus(SimpleGladeApp):
    event = None
    channel = None
    podcast = None
    thread = None

    def __init__(self, path="gpodder.glade",
                 root="gPodderStatus",
                 domain=app_name, **kwargs):
        path = os.path.join(glade_dir, path)
        SimpleGladeApp.__init__(self, path, root, domain, **kwargs)

    #-- Gpodderstatus.new {
    def new(self):
        if libgpodder.isDebugging():
            print "A new %s has been created" % self.__class__.__name__
    #-- Gpodderstatus.new }

    #-- Gpodderstatus custom methods {
    #   Write your own methods here
    def setup( self, channel, podcast):
        self.channel = channel
        self.podcast = podcast
        
        self.labelFrom.set_markup( "<b>" + self.channel.title + "</b>")
        self.labelFilename.set_markup( "<b>" + self.podcast.title + "</b>")
        
        filename = gPodderLib().getPodcastFilename( self.channel, self.podcast.url)

        if os.path.exists( filename) == False:
            self.event = Event()
            self.thread = downloadThread( self.podcast.url, filename, self.event)
            return True
        else:
            self.cancel()
            return False
    
    def download( self):
        self.thread.download()
        
        while self.event.isSet() == False:
            self.event.wait( 0.1)
            
            self.labelSpeed.set_text( self.thread.speed)
            self.progressBar.set_fraction( float(self.thread.percentage))
            
            while gtk.events_pending():
                gtk.main_iteration( False)

        self.gPodderStatus.destroy()
    
    def cancel( self):
        self.on_btnCancel_clicked( self.btnCancel, None)
    #-- Gpodderstatus custom methods }

    #-- Gpodderstatus.on_gPodderStatus_destroy {
    def on_gPodderStatus_destroy(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_gPodderStatus_destroy called with self.%s" % widget.get_name()
    #-- Gpodderstatus.on_gPodderStatus_destroy }

    #-- Gpodderstatus.on_btnCancel_clicked {
    def on_btnCancel_clicked(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_btnCancel_clicked called with self.%s" % widget.get_name()
        
        if self.thread != None:
            self.thread.cancel()

        while self.event != None and self.event.isSet() == False:
            None
        
        self.gPodderStatus.destroy()
    #-- Gpodderstatus.on_btnCancel_clicked }


class Gpodderchannel(SimpleGladeApp):
    waiting = None
    url = ""
    result = False
    
    def __init__(self, path="gpodder.glade",
                 root="gPodderChannel",
                 domain=app_name, **kwargs):
        path = os.path.join(glade_dir, path)
        SimpleGladeApp.__init__(self, path, root, domain, **kwargs)

    #-- Gpodderchannel.new {
    def new(self):
        if libgpodder.isDebugging():
            print "A new %s has been created" % self.__class__.__name__
    #-- Gpodderchannel.new }

    #-- Gpodderchannel custom methods {
    #   Write your own methods here
    def requestURL( self, message = None):
        if message != None:
            self.labelIntroduction.set_text( message)
        
        self.waiting = Event()
        while self.waiting.isSet() == False:
            self.waiting.wait( 0.01)
            while gtk.events_pending():
                gtk.main_iteration( False)

        if self.result == True:
            return self.url
        else:
            return None
    #-- Gpodderchannel custom methods }

    #-- Gpodderchannel.on_gPodderChannel_destroy {
    def on_gPodderChannel_destroy(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_gPodderChannel_destroy called with self.%s" % widget.get_name()
        self.result = False
        self.url = self.entryURL.get_text()
    #-- Gpodderchannel.on_gPodderChannel_destroy }

    #-- Gpodderchannel.on_btnOK_clicked {
    def on_btnOK_clicked(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_btnOK_clicked called with self.%s" % widget.get_name()
        self.gPodderChannel.destroy()
        self.result = True

        if self.waiting != None:
            self.waiting.set()
    #-- Gpodderchannel.on_btnOK_clicked }

    #-- Gpodderchannel.on_btnCancel_clicked {
    def on_btnCancel_clicked(self, widget, *args):
        if libgpodder.isDebugging():
            print "on_btnCancel_clicked called with self.%s" % widget.get_name()
        self.gPodderChannel.destroy()
        self.result = False
        
        if self.waiting != None:
            self.waiting.set()
    #-- Gpodderchannel.on_btnCancel_clicked }


#-- main {

def main( __version__ = None):
    global app_version
    
    gtk.gdk.threads_init()
    app_version = __version__
    g_podder = Gpodder()
    #g_podder_status = Gpodderstatus()
    #g_podder_channel = Gpodderchannel()

    g_podder.set_icon()
    g_podder.run()

if __name__ == "__main__":
    print "please run the gpodder binary, not this file"
    sys.exit( -1)

#-- main }
