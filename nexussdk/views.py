import json
from nexussdk.utils.http import http_get
from nexussdk.utils.http import http_put
from nexussdk.utils.http import http_post
from nexussdk.utils.http import http_delete
from urllib.parse import quote_plus as url_encode


ELASTIC_TYPE = "ElasticView"
SPARQL_TYPE = "SparqlView"

def create_es(org_label, project_label, view_data, id=None):
    """
        Creates an ElasticSearch view

        :param org_label: Label of the organization the view wil belong to
        :param project_label: label of the project the view will belong too
        :param view_data: Mapping data required for ElasticSearch indexing
        :return: The payload representing the view. This payload only contains the Nexus metadata
    """

    org_label = url_encode(org_label)
    project_label = url_encode(project_label)

    path = "/views/" + org_label + "/" + project_label

    # we give the possibility to use a JSON string instead of a dict
    if (not isinstance(view_data, dict)) and isinstance(view_data, str):
        view_data = json.loads(view_data)

    if "@type" not in view_data:
        view_data["@type"] = ["View", ELASTIC_TYPE, "Alpha"]

    if id is None:
        return http_post(path, body=view_data, use_base=True)
    else:
        view_id = url_encode(id)
        path = path + "/" + view_id
        return http_put(path, body=view_data, use_base=True)


def update_es(esview, rev=None):
    """
        Update a ElasticSearch view. The esview object is most likely the returned value of a
        nexus.views.fetch(), where some fields where modified, added or removed.
        Note that the returned payload only contains the Nexus metadata and not the
        complete view.

        :param esview: payload of a previously fetched view, with the modification to be updated
        :param rev: OPTIONAL The previous revision you want to update from.
        If not provided, the rev from the view argument will be used.
        :return: A payload containing only the Nexus metadata for this updated view.
    """

    if rev is None:
        rev = esview["_rev"]

    path = esview["_self"] + "?rev=" + str(rev)

    return http_put(path, esview, use_base=False)


def deprecate_es(esview, rev=None):
    """
        Update a ElasticSearch view. The esview object is most likely the returned value of a
        nexus.views.fetch(), where some fields where modified, added or removed.
        Note that the returned payload only contains the Nexus metadata and not the
        complete view.

        :param esview: payload of a previously fetched view, with the modification to be updated
        :param rev: OPTIONAL The previous revision you want to update from.
        If not provided, the rev from the view argument will be used.
        :return: A payload containing only the Nexus metadata for this updated view.
    """

    if rev is None:
        rev = esview["_rev"]

    path = esview["_self"] + "?rev=" + str(rev)

    return http_delete(path, esview, use_base=False)


def fetch(org_label, project_label, view_id, rev=None, tag=None):
    """
        Fetches a distant view and returns the payload as a dictionary.
        In case of error, an exception is thrown.

        :param org_label: The label of the organization that the view belongs to
        :param project_label: The label of the project that the view belongs to
        :param view_id: id of the view
        :param rev: OPTIONAL fetches a specific revision of a view (default: None, fetches the last)
        :param tag: OPTIONAL fetches the view version that has a specific tag (default: None)
        :return: Payload of the whole view as a dictionary
    """

    if rev is not None and tag is not None:
        raise Exception("The arguments rev and tag are mutually exclusive. One or the other must be chosen.")

    # the element composing the query URL need to be URL-encoded
    org_label = url_encode(org_label)
    project_label = url_encode(project_label)
    view_id = url_encode(view_id)

    path = "/views/" + org_label + "/" + project_label + "/" + view_id

    if rev is not None:
        path = path + "?rev=" + str(rev)

    if tag is not None:
        path = path + "?tag=" + str(tag)

    return http_get(path, use_base=True)


def list(org_label, project_label, pagination_from=0, pagination_size=20,
         deprecated=None, type = None, full_text_search_query=None):
    """
        List the views available for a given organization and project. All views, of all kinds.

        :param org_label: The label of the organization that the view belongs to
        :param project_label: The label of the project that the view belongs to
        :param pagination_from: OPTIONAL The pagination index to start from (default: 0)
        :param pagination_size: OPTIONAL The maximum number of elements to returns at once (default: 20)
        :param deprecated: OPTIONAL Get only deprecated view if True and get only non-deprecated results if False.
        If not specified (default), return both deprecated and not deprecated view.
        :param full_text_search_query: A string to look for as a full text query
        :return: The raw payload as a dictionary
    """

    org_label = url_encode(org_label)
    project_label = url_encode(project_label)

    path = "/views/" + org_label + "/" + project_label + "?from=" \
           + str(pagination_from) + "&size=" + str(pagination_size)

    if deprecated is not None:
        deprecated = "true" if deprecated else "false"
        path = path + "&deprecated=" + deprecated

    if type is not None:
        type = url_encode(type)
        path = path + "&type=" + type

    if full_text_search_query:
        full_text_search_query = url_encode(full_text_search_query)
        path = path + "&q=" + full_text_search_query

    return http_get(path, use_base=True)


def tag_es(esview, tag_value, rev_to_tag=None, rev=None):
    """
        Add a tag to a a specific revision of an ElasticSearch view. Note that a new revision (untagged) will be created

        :param esview: payload of a previously fetched view (ElasticSearch)
        :param tag_value: The value (or name) of a tag
        :param rev_to_tag: OPTIONAL Number of the revision to tag. If not provided, this will take the revision number
        from the provided resource payload.
        :param rev: OPTIONAL The previous revision you want to update from.
       If not provided, the rev from the resource argument will be used.
        :return: A payload containing only the Nexus metadata for this view.
    """

    if rev is None:
        rev = esview["_rev"]

    if rev_to_tag is None:
        rev_to_tag = esview["_rev"]

    path = esview["_self"] + "/tags?rev=" + str(rev)

    data = {
        "tag": tag_value,
        "rev": rev_to_tag
    }

    return http_put(path, body=data, use_base=False)


def aggregate_es(org_label, project_label, esviews, id):
    """
        Creates an aggregated view for ElasticSearch.

        :param org_label: Label of the organization the view wil belong to
        :param project_label: label of the project the view will belong too
        :param esviews: list of ElasticSearch view payloads, most likely got with .fetch()
        :param id: id to give to this aggregation id ElasticSearch views
        :return: A payload containing only the Nexus metadata for this aggregated view.
    """

    org_label = url_encode(org_label)
    project_label = url_encode(project_label)
    id = url_encode(id)

    path = "/views/" + org_label + "/" + project_label + "/" + id

    views_data = []

    for v in esviews:
        v_data = {
            "project": "/".join(v["_project"].split("/")[-2:]),
            "viewId":  v["@id"]
        }

        views_data.append(v_data)

    data = {
        "@context": {
            "nxv": "https://bluebrain.github.io/nexus/vocabulary/"
        },
        "@type": [
            "View",
            "AggregateElasticView",
            "Alpha"
        ],
        "views": views_data
    }

    return http_put(path, body=data, use_base=True)


def list_keep_only_es(viewlist):
    """
        Helper function to keep only the ElasticSearch views metadata from the result of a .list() call
        :param viewlist: the payload returned by .list()
        :return: the list of ElasticSearch view metadata (beware: not complete payloads like if it was the result of .fetch() calls)
    """
    return _filter_list_by_type(viewlist, ELASTIC_TYPE)


def list_keep_only_sparql(viewlist):
    """
        Helper function to keep only the SparQL views metadata from the result of a .list() call
        :param viewlist: the payload returned by .list()
        :return: the list of SparQL view metadata (beware: not complete payloads like if it was the result of .fetch() calls)
    """
    return _filter_list_by_type(viewlist, SPARQL_TYPE)


def _filter_list_by_type(list, type):
    new_list = []

    for el in list["_results"]:
        if ELASTIC_TYPE in el["@type"]:
            new_list.append(el)

    return new_list


def query_es(org_label, project_label, view_id, query):
    """
        Perform a ElasticSearch query

        :param org_label: Label of the organization to perform the query on
        :param project_label: Label of the project to perform the query on
        :param view_id: id of an ElasticSearch view
        :param query: ElasticSearch query as a JSON string or a dictionary
        :return: the result of the query as a dictionary
    """
    org_label = url_encode(org_label)
    project_label = url_encode(project_label)
    view_id = url_encode(view_id)

    path = "/views/" + org_label + "/" + project_label + "/" + view_id+  "/_search"

    if (not isinstance(query, dict)) and isinstance(query, str):
        query = json.loads(query)

    return http_post(path, body=query, use_base=True)


def query_sparql(org_label, project_label, query):
    """
        Perform a SparQL query.

        :param org_label: Label of the organization to perform the query on
        :param project_label: Label of the project to perform the query on
        :param query: Query as a string
        :return: result of the query as a dictionary
    """
    org_label = url_encode(org_label)
    project_label = url_encode(project_label)

    path = "/views/" + org_label + "/" + project_label + "/graph/sparql"

    return http_post(path, body=query, data_type="sparql", use_base=True)
