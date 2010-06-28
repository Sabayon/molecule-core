SUBDIRS = examples molecule po
PREFIX = /usr
BINDIR = $(PREFIX)/bin
DESTDIR = 
LIBDIR = $(PREFIX)/lib
SYSCONFDIR = /etc

all:
	for d in $(SUBDIRS); do $(MAKE) -C $$d; done

clean:
	for d in $(SUBDIRS); do $(MAKE) -C $$d clean; done

install:
	for d in $(SUBDIRS); do $(MAKE) -C $$d install; done
	# install the application
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 molecule.py $(DESTDIR)$(BINDIR)/molecule
