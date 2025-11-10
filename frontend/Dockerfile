FROM node:18
WORKDIR /usr/src/app
COPY frontend/package.json ./
RUN npm install
COPY frontend /usr/src/app
CMD ["npm", "start"]