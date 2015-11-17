# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
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

"""Record indexing related Celery tasks."""

import six
from invenio_celery import celery
from invenio_ext.es import es
from invenio_search.api import Query
from invenio_search.walkers.elasticsearch import ElasticSearchDSL

from invenio.base.globals import cfg

from ..signals import before_record_index


@before_record_index.connect
def populate_authors(recid, json):
    """ Populates a json record before indexing it to elastic.
        Adds a field for all the possible variations of an authors name
    """
    from invenio_records.tasks.tokenizer import BibIndexAuthorTokenizer
    tokenizer = BibIndexAuthorTokenizer()
    authors = json.get("authors")
    if authors is not None:
        for author in authors:
            name = author.get("full_name")
            if name is not None:
                author.update({"name_variations": tokenizer.tokenize(name)})


def get_record_index(record):
    """Decide which index the record should go to."""
    query = 'collection:"{collection}"'
    for collection, index in six.iteritems(
        cfg["SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING"]
    ):
        if Query(query.format(collection=collection)).match(record):
            return index


@celery.task
def index_record(recid, json):
    """Index a record in elasticsearch."""
    before_record_index.send(recid, json=json)
    index = get_record_index(json) or cfg['SEARCH_ELASTIC_DEFAULT_INDEX']
    before_record_index.send(recid, json=json)
    es.index(
        index=index,
        doc_type='record',
        body=json,
        id=recid
    )


@celery.task
def index_collection_percolator(name, dbquery):
    """Create an elasticsearch percolator for a given query."""
    indices = set(cfg["SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING"].values())
    indices.add(cfg['SEARCH_ELASTIC_DEFAULT_INDEX'])
    for index in indices:
        es.index(
            index=index,
            doc_type='.percolator',
            body={'query': Query(dbquery).query.accept(ElasticSearchDSL())},
            id=name
        )
