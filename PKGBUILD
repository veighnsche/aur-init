# Maintainer: Vince <vincepaul.liem@gmail.com>
pkgname=aur-init
pkgver=0.3.1
pkgrel=2
pkgdesc="Initialize an AUR package skeleton"
arch=('any')
depends=('python')
url="https://github.com/veighnsche/aur-init"
license=('MIT')
source=(
  "aur-init"
  "lib/aur_init.py"
  "templates/common/PKGBUILD.tmpl"
  "templates/common/ci.yml.tmpl"
)
sha256sums=(
  'SKIP'
  'SKIP'
  'SKIP'
  'SKIP'
  'SKIP'
)

package() {
  # Binary
  install -Dm755 "${srcdir}/aur-init" "${pkgdir}/usr/bin/aur-init"
  # Python library
  install -d "${pkgdir}/usr/lib/aur-init/lib"
  install -m 644 "${srcdir}/lib/aur_init.py" "${pkgdir}/usr/lib/aur-init/lib/aur_init.py"
  # Templates
  install -d "${pkgdir}/usr/share/aur-init/templates"
  cp -a "${srcdir}/templates/." "${pkgdir}/usr/share/aur-init/templates/"
}
