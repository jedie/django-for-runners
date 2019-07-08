FROM python:3.7
LABEL maintainer="Strubbl <Strubbl-Dockerfile@linux4tw.de>"

ENV RUNNER_DIR /home/runner
RUN \
  useradd runner && \
  mkdir -p ${RUNNER_DIR} && \
  chown -R runner:runner ${RUNNER_DIR}
WORKDIR ${RUNNER_DIR}
USER runner
RUN \
  wget https://raw.githubusercontent.com/jedie/django-for-runners/master/boot_django_for_runners.sh && \
  bash boot_django_for_runners.sh && \
  cd ${RUNNER_DIR}/Django-ForRunners/bin && \
  ./manage collectstatic

EXPOSE 8000

CMD cd ${RUNNER_DIR}/Django-ForRunners/bin && ./for_runners run-server 0.0.0.0:8000
