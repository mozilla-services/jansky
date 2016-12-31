# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from processor.util import utc_now
from processor.rule import Rule

import logging

logger = logging.getLogger(__name__)

# rules to change the internals of the raw crash
#
# s.p.mozilla_transform_rules.ESRVersionRewrite
# s.p.mozilla_transform_rules.PluginContentURL
# s.p.mozilla_transform_rules.PluginUserComment
# s.p.mozilla_transform_rules.FennecBetaError20150430


class ProductRule(Rule):
    '''transfers Product-related properties from the raw to the processed_crash,
    filling in with empty defaults where it
    '''

    def action(self, crash_id, raw_crash, dumps, processed_crash):
        processed_crash['product'] = raw_crash.get('ProductName', '')
        processed_crash['version'] = raw_crash.get('Version', '')
        processed_crash['productid'] = raw_crash.get('ProductID', '')
        processed_crash['distributor'] = raw_crash.get('Distributor', None)
        processed_crash['distributor_version'] = raw_crash.get(
            'Distributor_version',
            None
        )
        processed_crash['release_channel'] = raw_crash.get('ReleaseChannel', '')
        # redundant, but I want to exactly match old processors.
        processed_crash['ReleaseChannel'] = raw_crash.get('ReleaseChannel', '')
        processed_crash['build'] = raw_crash.get('BuildID', '')


class ProductRewrite(Rule):
    '''map a raw_crash ProductID to a ProductName using a lookup table
    '''

    def __init__(self):
        super(ProductRewrite, self).__init__()
        self.product_id_map = {
            # TODO: this is pulled from the database in processor2015
            # TODO: figure out what to do here instead, mocking for now
            # in processor2015 the value was a complex object built from a
            # sql table:
            #   'productid', 'product_name', 'rewrite'
            # simplified here, if we shouldn't rewrite it shouldn't be in
            # this lookup table
            '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}': 'FennecAndroid',
            '{ec8030f7-c20a-464f-9b0e-13b3a9e97384}': 'Chrome',
            '{ec8030f7-c20a-464f-9b0e-13c3a9e97384}': 'Safari',
        }

    def predicate(self, crash_id, raw_crash, dumps, processed_crash):
        return ('ProductID' in raw_crash
            and raw_crash['ProductID'] in self.product_id_map)

    def action(self, crash_id, raw_crash, dumps, processed_crash):
        product_id = raw_crash['ProductID']
        old_product_name = raw_crash['ProductName']
        new_product_name = self.product_id_map[product_id]

        raw_crash['ProductName'] = new_product_name

        logger.debug(
            'product name changed from %s to %s based '
            'on productID %s',
            old_product_name,
            new_product_name,
            product_id
        )