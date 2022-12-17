class Filt:
    def filt(self, image, meta, args):
        # check for + filters
        num_pos_filters = 0
        for arg in args:
            if arg[0] == '+':
                num_pos_filters += 1

        # no + filters
        if num_pos_filters == 0:
            for arg in args:
                if arg in meta['tags']:
                    return None, None
            return image, meta

        # has + filter
        cur_pos_filters = 0
        for arg in args:
            if arg[0] == '+':
                if arg[1:] in meta['tags']:
                    cur_pos_filters += 1
        if cur_pos_filters == num_pos_filters:
            return image, meta
        return None, None
