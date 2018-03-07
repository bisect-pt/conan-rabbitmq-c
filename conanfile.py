from conans import ConanFile, CMake, tools

class RabbitmqcConan(ConanFile):
    name = "rabbitmq-c"
    version = "0.8.0"
    license = "https://github.com/alanxz/rabbitmq-c/blob/master/LICENSE-MIT"
    url = "https://github.com/alanxz/rabbitmq-c"
    description = "C-language AMQP client library for RabbitMQ"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "no_openssl": [True, False]
    }
    default_options = "shared=False", "no_openssl=True"
    generators = "cmake"
    unzipped_name = "rabbitmq-c-%s" % version

    def requirements(self):
        if not self.options.no_openssl:
            self.requires.add("OpenSSL/1.0.2m@conan/stable")

    def source(self):
        zip_name = "%s.tar.gz" % self.unzipped_name
        download_url = "%s/releases/download/v%s/%s" % (self.url, self.version, zip_name)

        tools.download(download_url, zip_name)
        tools.unzip(zip_name)

    def build(self):
        cmake = CMake(self)

        if not self.options.no_openssl:
            cmake.definitions['ENABLE_SSL_SUPPORT'] = "ON"
            cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info["OpenSSL"].rootpath
        else:
            cmake.definitions['ENABLE_SSL_SUPPORT'] = "OFF"

        cmake.definitions['BUILD_EXAMPLES'] = "OFF"
        cmake.definitions['BUILD_TESTS'] = "OFF"
        cmake.definitions['BUILD_TOOLS'] = "OFF"
        cmake.definitions['ENABLE_DOC'] = "OFF"

        if self.options.shared:
            cmake.definitions['BUILD_SHARED_LIBS'] = True
            cmake.definitions['BUILD_STATIC_LIBS'] = False
        else:
            cmake.definitions['BUILD_STATIC_LIBS'] = True
            cmake.definitions['BUILD_SHARED_LIBS'] = False

        cmake.configure(source_folder=self.unzipped_name, build_folder=self.unzipped_name)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*.h", dst="include", src=self.unzipped_name)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

        # Copy cmake find_package script into project -> we need to do one
        # self.copy("FindRabbitmq.cmake", ".", ".")

        # Copying debug symbols
#        if self.settings.compiler == "Visual Studio" and self.options.include_pdbs:
#            self.copy(pattern="*.pdb", dst="lib", src=".", keep_path=False)

    def package_info(self):

        if self.settings.os == "Linux":
            self.cpp_info.libs = ["rabbitmq", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.libs = ["librabbitmq.4.lib"]
        else:
            self.cpp_info.libs = ["rabbitmq"]

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32.lib")

            # Need to link with crypt32 as well for OpenSSL
            if not self.options.no_openssl:
                self.cpp_info.libs.append("crypt32")
