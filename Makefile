SUBDIRS = examples molecule
PREFIX = /usr
BINDIR = $(PREFIX)/bin
DESTDIR = 
LIBDIR = $(PREFIX)/lib
SYSCONFDIR = /etc

all:
	for d in $(SUBDIRS); do make -C $$d; done

clean:
	for d in $(SUBDIRS); do make -C $$d clean; done

install:
	for d in $(SUBDIRS); do make -C $$d install; done
	# install the application
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 molecule.py $(DESTDIR)$(BINDIR)/molecule