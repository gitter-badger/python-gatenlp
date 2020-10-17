"""
A simple class that represents a collection of sorted intervals and allows for some basic interval-based
operations. Internally this stores the intervals using standard sorted lists. This is not optimal and my
incur a O(n) overhead on some operations depending on the result set. It also may incur a significant overhead
for creating and maintaning the sorted lists.
NOTE: this stores a tuple (start, end, object) in the sorted list and uses a key function that returns the offset
for sorting.

!!!TODO: we should maybe implement a stricter and more stable sorting order here, where
we use the sorting order defined in the annotation class itself.
"""

import sys
from sortedcontainers import SortedKeyList


class SortedIntvls:
    """ """
    def __init__(self):
        # NOTE: we sort by increasing start offset then increasing annotation id for this
        self._by_start = SortedKeyList(key=lambda x: (x[0], x[2]))
        # for this we sort by end offset only
        self._by_end = SortedKeyList(key=lambda x: x[1])

    def add(self, start, end, data):
        """

        Args:
          start: 
          end: 
          data: 

        Returns:

        """
        self._by_start.add((start, end, data))
        self._by_end.add((start, end, data))

    def update(self, tupleiterable):
        """

        Args:
          tupleiterable: 

        Returns:

        """
        self._by_start.update(tupleiterable)
        self._by_end.update(tupleiterable)

    def remove(self, start, end, data):
        """

        Args:
          start: 
          end: 
          data: 

        Returns:

        """
        self._by_start.remove((start, end, data))
        self._by_end.remove((start, end, data))

    def discard(self, start, end, data):
        """

        Args:
          start: 
          end: 
          data: 

        Returns:

        """
        self._by_start.discard((start, end, data))
        self._by_end.discard((start, end, data))

    def __len__(self):
        return len(self._by_start)

    def starting_at(self, offset):
        """Return an iterable of (start, end, data) tuples where start==offset

        Args:
          offset: the starting offset

        Returns:
          

        """
        return self._by_start.irange_key(min_key=(offset, 0), max_key=(offset,sys.maxsize))

    def ending_at(self, offset):
        """Return an iterable of (start, end, data) tuples where end==offset

        Args:
          offset: the ending offset

        Returns:
          

        """
        return self._by_end.irange_key(min_key=offset, max_key=offset)

    def at(self, start, end):
        """Return iterable of tuples where start==start and end==end

        Args:
          start: param end
          end: 

        Returns:
          

        """
        for intvl in self._by_start.irange_key(min_key=(start,0), max_key=(start, sys.maxsize)):
            if intvl[1] == end:
                yield intvl

    # SAME as within
    def within(self, start, end):
        """Return intervals which are fully contained within start...end

        Args:
          start: param end
          end: 

        Returns:
          

        """
        # get all the intervals that start within the range, then keep those which also end within the range
        for intvl in self._by_start.irange_key(min_key=(start,0), max_key=(end, sys.maxsize)):
            if intvl[1] <= end:
                yield intvl

    def starting_from(self, offset):
        """Intervals that start at or after offset.

        Args:
          offset: return:

        Returns:

        """
        return self._by_start.irange_key(min_key=(offset,0))

    def starting_before(self, offset):
        """Intervals that start before offset

        Args:
          offset: return:

        Returns:

        """
        return self._by_start.irange_key(max_key=(offset-1, sys.maxsize))

    def ending_to(self, offset):
        """Intervals that end before or at the given end offset.
        
        NOTE: the result is sorted by end offset, not start offset!

        Args:
          offset: return:

        Returns:

        """
        return self._by_end.irange_key(max_key=offset)

    def ending_after(self, offset):
        """Intervals the end after the given offset
        
        NOTE: the result is sorted by end offset!

        Args:
          offset: return:

        Returns:

        """
        return self._by_end.irange_key(min_key=offset+1)

    def covering(self, start, end):
        """Intervals that contain the given range

        Args:
          start: param end:
          end: 

        Returns:

        """
        # All intervals that start at or before the start and end at or after the end offset
        # we do this by first getting the intervals the start before or atthe start
        # then filtering by end
        for intvl in self._by_start.irange_key(max_key=(start, sys.maxsize)):
            if intvl[1] >= end:
                yield intvl

    def overlapping(self, start, end):
        """Intervals that overlap with the given range.

        Args:
          start: param end:
          end: 

        Returns:

        """
        # All intervals where the start or end offset lies within the given range.
        # This excludes the ones where the end offset is before the start or
        # where the start offset is after the end of the range.
        # Here we do this by looking at all intervals where the start offset is before the
        # end of the range. This still includes those which also end before the start of the range
        # so we check in addition that the end is larger than the start of the range.
        for intvl in self._by_start.irange_key(max_key=(end-1, sys.maxsize)):
            if intvl[1] > start+1:
                yield intvl

    def firsts(self):
        """

        Args:

        Returns:
          : return:

        """
        laststart = None
        # logger.info("DEBUG: set laststart to None")
        for intvl in self._by_start.irange_key():
            # logger.info("DEBUG: checking interval {}".format(intvl))
            if laststart is None:
                laststart = intvl[0]
                # logger.info("DEBUG: setting laststart to {} and yielding {}".format(intvl[0], intvl))
                yield intvl
            elif intvl[0] == laststart:
                # logger.info("DEBUG: yielding {}".format(intvl))
                yield intvl
            else:
                # logger.info("DEBUG: returning since we got {}".format(intvl))
                return

    def lasts(self):
        """

        Args:

        Returns:
          : return:

        """
        laststart = None
        for intvl in reversed(self._by_start):
            if laststart is None:
                laststart = intvl[0]
                yield intvl
            elif intvl[0] == laststart:
                yield intvl
            else:
                return

    def min_start(self):
        """Returns the smallest start offset we have
        
        :return:

        Args:

        Returns:

        """
        return self._by_start[0][0]

    def max_end(self):
        """Returns the biggest end offset we have
        
        :return:

        Args:

        Returns:

        """
        return self._by_end[-1][1]

    def irange(self, minoff=None, maxoff=None, reverse=False):
        """

        Args:
          minoff: (Default value = None)
          maxoff: (Default value = None)
          reverse: (Default value = False)

        Returns:

        """
        return self._by_start.irange_key(min_key=minoff, max_key=maxoff, reverse=reverse)

    def __repr__(self):
        return "SortedIntvls({},{})".format(self._by_start, self._by_end)
