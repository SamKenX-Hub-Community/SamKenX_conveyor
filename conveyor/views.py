# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib.parse

from aiohttp import web


async def redirect(request):
    python_version = request.match_info["python_version"]
    project_l = request.match_info["project_l"]
    project_name = request.match_info["project_name"]
    filename = request.match_info["filename"]

    # If the letter bucket doesn't match the first letter of the project, then
    # there is no point to going any further since it will be a 404 regardless.
    if project_l != project_name[0]:
        return web.Response(status=404)

    # If the filename we're looking for is a signature, then we'll need to turn
    # this into the *real* filename and a note that we're looking for the
    # signature.
    if filename.endswith(".asc"):
        filename = filename[:-4]
        signature = True
    else:
        signature = False

    json_url = urllib.parse.urljoin(
        request.app["settings"]["endpoint"],
        "/pypi/{}/json".format(project_name),
    )

    async with request.app["http.session"].get(json_url) as resp:
        if 400 <= resp.status < 500:
            return web.Response(status=resp.status)
        elif 500 <= resp.status < 600:
            return web.Response(status=503)

        # It shouldn't be possible to get a status code other than 200 here.
        assert resp.status == 200

        # Get the JSON data from our request.
        data = await resp.json()

    # Look at all of the files listed in the JSON response, and see if one
    # matches our filename and Python version. If we find one, then return a
    # 302 redirect to that URL.
    for release in data.get("releases", {}).values():
        for file_ in release:
            if (file_["filename"] == filename
                    and file_["python_version"] == python_version):
                # If we've found our filename, but we were actually looking for
                # the *signature* of that file, then we need to check if it has
                # a signature associated with it, and if so redirect to that,
                # and if not return a 404.
                if signature:
                    if file_.get("has_sig"):
                        return web.Response(
                            status=302,
                            headers={
                                "Location": file_["url"] + ".asc",
                                "Cache-Control": "max-age=604800, public",
                            },
                        )
                    else:
                        return web.Response(status=404)
                # If we've found our filename, then we'll redirect to it.
                else:
                    return web.Response(
                        status=302,
                        headers={
                            "Location": file_["url"],
                            "Cache-Control": "max-age=604800, public",
                        },
                    )

    # If we've gotten to this point, it means that we couldn't locate an url
    # to redirect to so we'll jsut 404.
    return web.Response(status=404)
