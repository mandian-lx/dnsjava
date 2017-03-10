%{?_javapackages_macros:%_javapackages_macros}

Name:		dnsjava
Version:	2.1.8
Release:	1
Summary:	An implementation of DNS in Java
Group:		Development/Java
License:	BSD and MIT
URL:		http://www.dnsjava.org/
Source0:	http://www.dnsjava.org/download/%{name}-%{version}.tar.gz
Source1:	https://repo1.maven.org/maven2/dnsjava/%{name}/%{version}/%{name}-%{version}.pom
Patch0:		https://github.com/jitsi/libsrc/raw/master/dnsjava-dnssec.patch
BuildArch:	noarch

BuildRequires:	maven-local
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:	mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires:	mvn(org.sonatype.oss:oss-parent:pom:)

%description
dnsjava is an implementation of DNS in Java. It supports all defined record
types (including the DNSSEC types), and unknown types. It can be used for
queries, zone transfers, and dynamic updates. It includes a cache which can
be used by clients, and a minimal implementation of a server. It supports
TSIG authenticated messages, partial DNSSEC verification, and EDNS0.

dnsjava provides functionality above and beyond that of the InetAddress
class. Since it is written in pure Java, dnsjava is fully threadable, and in
many cases is faster than using InetAddress.

dnsjava provides both high and low level access to DNS. The high level
functions perform queries for records of a given name, type, and class, and
return the answer or reason for failure. There are also functions similar to
those in the InetAddress class. A cache is used to reduce the number of DNS
queries sent. The low level functions allow direct manipulation of DNS
messages and records, as well as allowing additional resolver properties to
be set.

A simple tool for doing DNS lookups, a 'dig' clone and a dynamic update client 
are included, as well as a simple authoritative-only server. 

%files -f .mfiles
%doc README
%doc Changelog
%doc USAGE
%doc examples.html
%doc *java
%doc LICENSE

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------


%prep
%setup -q
# Delete all prebuild JARs and classes
find . -name "*.jar" -delete
find . -name "*.class" -delete

# Delete prebuild docs
rm -fr doc

# Apply all patches
%patch0 -p0 -b .orig

# Copy the pom.xml file in the right place
cp %{SOURCE1} ./pom.xml

# Fix file-not-utf8 warning
iconv -f iso8859-1 -t utf8 Changelog > Changelog.tmp
touch -r Changelog Changelog.tmp
mv -f Changelog.tmp Changelog

# Remove unused maven plugin
%pom_remove_plugin :maven-gpg-plugin

# Add an OSGi compilant MANIFEST.MF
%pom_xpath_inject "pom:project" "<packaging>bundle</packaging>" .
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" \
	"<extensions>true</extensions>"

# Add the META-INF/INDEX.LIST (fix jar-not-indexed warning) and
# the META-INF/MANIFEST.MF to the jar archive
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-jar-plugin']]" "
<executions>
	<execution>
		<phase>package</phase>
		<configuration>
			<archive>
				<manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
				<manifest>
					<addDefaultImplementationEntries>true</addDefaultImplementationEntries>
					<addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
				</manifest>
				<index>true</index>
			</archive>
		</configuration>
		<goals>
			<goal>jar</goal>
		</goals>
	</execution>
</executions>"

# Remove failing tests
#   require a vaild connection
%pom_add_plugin :maven-surefire-plugin . "
<configuration>
	<excludes>
		<exclude>**/AddressTest.java</exclude>
		<exclude>**/CompressionTest.java</exclude>
		<exclude>**/NameTest.java</exclude>
	</excludes>
</configuration>"

# Fix jar name
%mvn_file :%{name} %{name}-%{version} %{name}

%build
%mvn_build

# remove script
rm -f .xmvn/apidocs/javadoc.sh

%install
%mvn_install

