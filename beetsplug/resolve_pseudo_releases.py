from beets.autotag.hooks import AlbumInfo
from beets.plugins import BeetsPlugin
from beets.autotag import mb 

class ResolvePseudoReleases(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.register_listener('albuminfo_received', self.albuminfo_received)

    def albuminfo_received(self, info: AlbumInfo):
        if info['albumstatus'] == 'Pseudo-Release':
            actual_id = self._get_actual_release_id(info.album_id)
            actual = self._fetch_actual_release_data(actual_id)
            info.update(actual)
        return {}

    def _get_actual_release_id(self, id):
        pseudo_rel = mb.musicbrainzngs.get_release_by_id(id, includes=['release-rels'])
        relations = filter_related_releases(pseudo_rel['release']["release-relation-list"])
        if len(relations) > 1:
            self._log.error('pseudo relase is linked to multiple actual relases: {}'.format(id))
        
        if len(relations) > 0:
            return relations[0]['target']

        return None 
    
    def _fetch_actual_release_data(self, id):
        release: AlbumInfo = mb.album_for_id(id)
        # TODO maybe only return a list of supported fields?
        del release['tracks']
        del release["album_id"]
        del release["artist_id"]
        del release["album"]
        del release["artist"]
        del release["artist_credit"]
        del release["artist_sort"]
        del release["albumdisambig"]
        del release["albumstatus"]
        # should already be in the pseudo
        del release["releasegroup_id"]
        # script and langugage are meant for the tracklist
        del release["language"]
        del release["script"]
        return release


def filter_related_releases(relations):
    result = []
    for relation in relations:
        if relation["type"] == "transl-tracklisting" and relation['direction'] == "backward":
            result.append(relation)
    return result
    
