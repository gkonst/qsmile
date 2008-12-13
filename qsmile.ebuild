# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header:

inherit eutils distutils

DESCRIPTION="Smile Manager for Instant Messangers."
HOMEPAGE="http://code.google.com/p/qsmile/"
SRC_URI=""

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~ppc ~x86"
IUSE=""

DEPEND=">=dev-lang/python-2.5
    dev-python/PyQt4"
RDEPEND="${DEPEND}"

pkg_setup() {
}

src_install() {
	distutils_src_install
}

pkg_postinst() {
}
