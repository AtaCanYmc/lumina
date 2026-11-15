class Lumina < Formula
  include Language::Python::Virtualenv

  desc "Lithophane and Spiral Betty 3D Art Generator CLI"
  homepage "https://github.com/AtaCanYmc/lumina"
  url "https://files.pythonhosted.org/packages/16/7f/7c08b9d8064b41a6807bdf3dfd8cd2b8d352871139233314d98f860ccb05/lumina_tools-1.0.0.tar.gz"
  sha256 "08c1a72dfcc59dbfe4ab23dd3fa511160ab1a30cc4c6b92fd1b2485eceb908d8"
  license "MIT"

  depends_on "numpy"
  depends_on "opencv"
  depends_on "python@3.12"

  resource "click" do
    url "https://files.pythonhosted.org/packages/45/37/edbf1b0707709013c0cf2e8317e03d97ed29bf4cac709fe328904ae92a38/click-8.5.1.tar.gz"
    sha256 "9bbfada76703fd1d784b83eea012e3e8c6a001a876543ef104fa56aaaeb072b4"
  end

  resource "numpy-stl" do
    url "https://files.pythonhosted.org/packages/56/61/14bd181fec28d1bc268de2a3ce179bb7bdd1ef4152637b1c4a74d048c69c/numpy_stl-4.1.4.tar.gz"
    sha256 "d3985564c49a40e1ab7f07f8f85ee8ef8bef906f762f20cef377f1cdf6895d36"
  end

  resource "python-utils" do
    url "https://files.pythonhosted.org/packages/f6/bf/e4cc07248ca65fe5065a9712efeace1eba6b0c77c72fc24cbfc8a79ddd80/python_utils-4.2.2.tar.gz"
    sha256 "6c51c46e600c67ad5f16c4205ba875ced4372e560561c5aa3cf52ff1d4657471"
  end

  def install
    venv = virtualenv_create(libexec, "python@3.12", system_site_packages: true)
    venv.pip_install resources
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "Lumina", shell_output("#{bin}/lumina --help")
  end
end
