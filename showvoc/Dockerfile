FROM eclipse-temurin:21-jre-alpine-3.24

ENV sv_version=6.1.2

RUN wget -O /tmp/showvoc.zip https://bitbucket.org/art-uniroma2/showvoc/downloads/showvoc-${sv_version}-full.zip

RUN busybox unzip /tmp/showvoc.zip -d /opt

RUN rm /tmp/showvoc.zip

RUN mv /opt/semanticturkey-* /opt/semanticturkey

CMD ["sh", "/opt/semanticturkey/bin/semanticturkey.sh"]
