#!/bin/bash
tar -xvjf datasets/mbdump.tar.bz2 mbdump/genre mbdump/genre_alias mbdump/genre_alias_type mbdump/l_genre_genre
mv mbdump/* datasets/
rmdir mbdump