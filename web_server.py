# Base classes for the various micro services infrastrure web servers
# (control, gatekeeper, FailHandler).
# 

import BaseHTTPServer
import httplib
import json
import SocketServer
import urlparse


# An exception we can reliably catch. Thrown by web_error(),
# unauthorized(), not_found(), etc. Should be caught at the outer most
# level of the handle. web_error() and ignored. web_error() will have
# already logged the message, and we don't want to clutter the log
# with stack traces for these expected errors.
#
class RequestException(Exception):
    pass

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

class BaseHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def enter_request(self):
        """Basic logging to do at the start of any request."""

        self.log_message("Command: %s Path: %s Headers: %r",
                         self.command, self.path, self.headers.items())


    def check_https(self, authenticator, options):
        """Enforce HTTPS use.

           If options.allow_http is True return True.

           Otherwise return True iff the current request was made over
           HTTPS (based on the x-forwarded-proto header).

           If options.allow_http is False, and this request was not done
           over HTTPS, then invalidate the passed authenticator.

           authenticator may be None.
        """

        if options.allow_http:
            return True

        if "x-forwarded-proto" not in self.headers:
            authentication.forget_authenticator(authenticator)
            return False

        proto = self.headers.getheader('x-forwarded-proto')
        proto = proto.lower()
        if 'https' != proto:
            authentication.forget_authenticator(authenticator)
            return False

        return True

    def web_error(self, code, message_format="", *args):
        message = message_format%args
        self.send_error(code, message)
        message = "%s %s %s: %s"%(
            self.command, self.path, code, message)
        self.log_message(message)
        raise RequestException(message)

    def unauthorized(self, message_format="", *args):
        self.web_error(httplib.UNAUTHORIZED, message_format, *args)

    def not_found(self):
        self.web_error(httplib.NOT_FOUND, "Page Not Found: %s", self.path)

    def parse_content_length(self):
        content_len = self.headers.getheader('content-length')
        try:
            return int(content_len)
        except:
            self.web_error(httplib.BAD_REQUEST, "No / invalid content-length header %s", content_len)

    def read_request_body(self):
        return self.rfile.read(self.parse_content_length())

    def read_x_www_form_urlencoded_request_body(self):
        if self.headers.gettype() != "application/x-www-form-urlencoded":
            self.web_error(httplib.UNSUPPORTED_MEDIA_TYPE, "Unsupported Content-type:" + self.headers.gettype())

        raw_body = self.read_request_body()
        return urlparse.parse_qs(raw_body)

    def read_json_request_body(self):
        if self.headers.gettype() != "application/json":
            self.web_error(httplib.UNSUPPORTED_MEDIA_TYPE, "Unsupported Content-type:" + self.headers.gettype())

        raw_body = self.read_request_body()
        try:
            return json.loads(raw_body)
        except ValueError as e:
            self.web_error(httplib.BAD_REQUEST, "Porly formed JSON: %s,", e.message)

    def single_value(self, table, key, from_what, default=None):
        if key not in table:
            return default

        v = table[key]
        if len(v) == 1:
            return v[0]
        elif len(v) == 0:
            return default
        else:
            self.web_error(httplib.BAD_REQUEST, "Too many values for %s in %s", key, from_what)
