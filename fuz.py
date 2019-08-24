"""
FuzClass

A new and improved way of programming has finally arrived!

Natural language is fuzzy. Oftentimes, we mean 'foobar', but write something
like 'fubar'. A simple, harmless typo! Why should the computer complain and be
so annoyingly picky? Instead, could it not help us by recognizing what we
really meant and just quitely correct such innocent typos?

With FuzClass we finally have relief! At last, the full potential of the
computer is unleashed. Instead of bothering us with aannoying attribute-errors
all the time, we can finally allow it to actually be of help while we are
developing.

Say goodbye to typo-induced attribute errors, once and for all!

Requirements: The 'fuzzy' package. Install with: pip install fuzzy

(c) Juergen Brendel, 2014, 2019

"""

import fuzzy

class FuzClass:
    """
    Typo-friendly class.

    Instead of raising AttributeErrors, it simply looks amongst already
    existing attributes to find any that sound similar to what we typed.

    Works for getting as well as setting of attributes.

    """

    def _off_limits(self, name):
        """
        Test if this is a name we want to mess with.

        Short names, or names starting with '_' are protected from our
        shenanigans.

        """
        return name[0] == "_" or len(name) < 2

    def _get_name_sound(self, name):
        """
        Convert a name to its 'sound'.

        We use the 'fuzzy' module, which offers different algorithsm to find the phontics of a
        text.

        """
        dmo                 = fuzzy.DMetaphone()
        name_sound_bytes, _ = dmo(name)
        name_sound          = name_sound_bytes.decode()
        return name_sound

    def _find_similar_attr(self, name):
        """
        Find an attribute that sounds or is similar to the specified name.

        We return either the name of an existing attribute with a similar name,
        or - if nothing is found - just the name that was specified here.

        'similar' here means: It either sounds similar, or the spelling is
        similar enough (same start and end letter, but inner letters can be
        jumbled).

        """
        # We are not considering really short names or names that start with an
        # underscore.
        if not self._off_limits(name):

            # These are the actually existing names in the class (we also only
            # consider those that don't start with _ and have a minimum length).
            existing_attrs = [a for a in dir(self) if not self._off_limits(a)]

            # Also make version of all lower characters
            existing_attrs_lower = [a.lower() for a in existing_attrs]

            # Maybe everything else is similar, it's just the capitalization
            # that's off? And if not that, maybe it's just that the inner
            # letters of the attribute name were jumbled?
            name_lower              = name.lower()
            specified_inner_letters = set(name_lower[1:-1])
            for i, attr_lower in enumerate(existing_attrs_lower):
                # Check if we have an exact match if we ignore capitalization,
                # of if the inner letters match closely enough (an extra or
                # missing letter is allowed)
                attr_inner_letters = set(attr_lower[1:-1])
                different_inner_letters = \
                     specified_inner_letters.symmetric_difference(
                                                            attr_inner_letters)
                if attr_lower == name_lower  or  \
                        (attr_lower[0] == name_lower[0] and
                         attr_lower[-1] == name_lower[-1] and
                         len(different_inner_letters) < 2):
                    # Existing lower attrs are in same order as original
                    # existing attrs. Thus, the position of this match is the
                    # correct one to find the original attr name in the original
                    # existing attrs list.
                    return existing_attrs[i]

            # Now check if we find any attributes that at least sound like
            # what we specified.
            # Find what the name 'sounds like'.
            name_sound = self._get_name_sound(name)
            if name_sound:
                for attr in existing_attrs:
                    # Compare the sound of the specified attribute name with the
                    # sounds of any exiting attributes. I guess we could cache
                    # the sounds of the existing attributes somewhere, if we
                    # don't mind spending some RAM on that.
                    existing_attr_name_sound = self._get_name_sound(attr)
                    if existing_attr_name_sound == name_sound:
                        # Yay! Found a similar sounding attribute. This must b#e
                        # what the developer really meant! We know better... :-)
                        return attr

        return name

    def __setattr__(self, name, value):
        """
        When setting an attribute, we first see whether a similar sounding one
        exists already. If so, we just assign the value to that one instead!

        It was probably just a typo, so we're just trying to help out.

        """
        new_name = self._find_similar_attr(name)
        super(FuzClass, self).__setattr__(new_name, value)

    def __getattr__(self, name):
        """
        Before complaining about not being able to find an attribute, we just
        see if maybe the developer just made a typo. If there is an attribute
        already that sounds similar, we will just return that one instead!

        """
        new_name = self._find_similar_attr(name)
        if new_name == name:
            raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))
        else:
            return super().__getattribute__(new_name)

#
# Demo of the new and improved attribute handling...
#
if __name__ == "__main__":
    # Defining a new and improved typo-friendly class...
    class MyTest(FuzClass):
        pass
    # Testing some attribute accesses to confirm
    m = MyTest()
    print("Setting 'foobar' to 123.")
    m.foobar = 123
    print("'foobar' should be 123:     ", m.foobar)
    print("'fubar' should also be 123: ", m.fubar)
    print("Now setting 'fuhbar' to 456.")
    m.fuhbar = 456
    print("'foobar' should now be 456: ", m.foobar)
