#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime as dt


class datetime( dt.datetime ):
    def __divmod__( self, delta ):
        seconds = ( self - dt.datetime.min  ).total_seconds()
        remainder = dt.timedelta( seconds = seconds % delta.total_seconds() )
        quotient = self - remainder
        return quotient, remainder

    def __floordiv__( self, delta ):
        return divmod( self, delta )[0]

    def __mod__( self, delta ):
        return divmod( self, delta )[1]