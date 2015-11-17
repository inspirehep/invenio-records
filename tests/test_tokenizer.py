# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by theF ree Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio_testing import InvenioTestCase


class TokenizerTest(InvenioTestCase):

    def test_tokenizer(self):
        from invenio_ext.es import es
        from invenio_records.tasks.tokenizer import BibIndexAuthorTokenizer
        rec = es.get(index='hep', id=232935)
        rec_list = rec['_source']['authors'][0]['name_variations']
        name = rec['_source']['authors'][0]['full_name']
        tokenizer = BibIndexAuthorTokenizer()
        token_list = tokenizer.tokenize(name)
        self.assertEqual(token_list, rec_list)
