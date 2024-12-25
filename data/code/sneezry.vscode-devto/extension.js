(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
class DevApiKeyManager {
    constructor(_context, _api) {
        this._context = _context;
        this._api = _api;
    }
    updateApiKey(apiKey) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this._context.globalState.update('devto:apiKey', apiKey);
            return apiKey;
        });
    }
    getApiKey() {
        return __awaiter(this, void 0, void 0, function* () {
            const apiKey = this._context.globalState.get('devto:apiKey');
            if (apiKey) {
                yield vscode.commands.executeCommand('setContext', 'devto:authorized', true);
            }
            else {
                yield vscode.commands.executeCommand('setContext', 'devto:authorized', false);
            }
            return apiKey;
        });
    }
    updateApiKeyCommand(callback) {
        return __awaiter(this, void 0, void 0, function* () {
            const apiKey = yield this.getApiKey();
            const newApiKey = yield vscode.window.showInputBox({
                value: apiKey,
                prompt: 'DEV Community API key',
                ignoreFocusOut: true,
            });
            if (newApiKey !== undefined) {
                yield this.updateApiKey(newApiKey);
                this._api.updateApiKey(newApiKey);
                if (newApiKey) {
                    yield vscode.commands.executeCommand('setContext', 'devto:authorized', true);
                }
                else {
                    yield vscode.commands.executeCommand('setContext', 'devto:authorized', false);
                }
                callback();
            }
        });
    }
    removeApiKeyCommand(callback) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.updateApiKey('');
            this._api.updateApiKey('');
            yield vscode.commands.executeCommand('setContext', 'devto:authorized', false);
            callback();
        });
    }
}
exports.DevApiKeyManager = DevApiKeyManager;

},{"vscode":undefined}],2:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const GitHubApi_1 = require("./api/GitHubApi");
const ImgurApi_1 = require("./api/ImgurApi");
const path = require("path");
class ImageUploadManager {
    constructor(_context) {
        this._context = _context;
        const personalToken = this._getGitHubPersonalToken();
        this._gitHubAPI = new GitHubApi_1.GitHubAPI(personalToken);
    }
    _getGitHubPersonalToken() {
        const token = this._context.globalState.get('devto:gitHubToken');
        return token;
    }
    updateGitHubPersonalToken() {
        return __awaiter(this, void 0, void 0, function* () {
            const personalToken = this._getGitHubPersonalToken();
            const newPersonalToken = yield vscode.window.showInputBox({
                value: personalToken,
                prompt: 'GitHub personal access token',
                ignoreFocusOut: true,
            });
            if (newPersonalToken === undefined) {
                return undefined;
            }
            yield this._context.globalState.update('devto:gitHubToken', newPersonalToken);
            return newPersonalToken;
        });
    }
    removeGitHubPersonalToken() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this._context.globalState.update('devto:gitHubToken', '');
        });
    }
    uploadImage() {
        return __awaiter(this, void 0, void 0, function* () {
            const imageFileUri = yield vscode.window.showOpenDialog({
                canSelectMany: false,
                filters: {
                    'Images': ['png', 'jpg', 'gif', 'bmp', 'webp', 'svg'],
                }
            });
            if (imageFileUri) {
                const personalToken = this._getGitHubPersonalToken();
                const uri = imageFileUri[0];
                const imageFileName = path.basename(uri.fsPath);
                vscode.window.withProgress({
                    title: `Uploading ${imageFileName} to ${personalToken ? 'GitHub' : 'Imgur'}`,
                    location: vscode.ProgressLocation.Notification,
                }, () => __awaiter(this, void 0, void 0, function* () {
                    let url;
                    if (!personalToken) {
                        const response = yield ImgurApi_1.ImgurAPI.upload(uri);
                        url = response.data.link;
                    }
                    else {
                        const response = yield this._gitHubAPI.upload(uri);
                        url = response.content.download_url;
                    }
                    const editor = vscode.window.activeTextEditor;
                    if (editor && editor.document.uri.scheme === 'devto') {
                        const position = editor.selection.active;
                        const snippet = new vscode.SnippetString(`![](${url})`);
                        editor.insertSnippet(snippet, position);
                    }
                }));
            }
        });
    }
}
exports.ImageUploadManager = ImageUploadManager;

},{"./api/GitHubApi":4,"./api/ImgurApi":5,"path":undefined,"vscode":undefined}],3:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const rq = require("request-promise");
class DevAPI {
    constructor(_apiKey) {
        this._apiKey = _apiKey;
    }
    _buildRequestOptions(path, method, parameters, article) {
        let uri = `https://dev.to/api${path}`;
        if (parameters) {
            let query = [];
            for (const parameterKey of Object.keys(parameters)) {
                query.push(`${parameterKey}=${parameters[parameterKey]}`);
            }
            uri += `?${query.join('&')}`;
        }
        const options = {
            uri,
            headers: {
                'User-Agent': 'vscode-devto;https://marketplace.visualstudio.com/items?itemName=sneezry.vscode-devto',
                'api-key': this._apiKey,
            },
            method,
            json: true,
        };
        if (article) {
            options.body = { article };
        }
        return options;
    }
    _list(page) {
        return __awaiter(this, void 0, void 0, function* () {
            const options = this._buildRequestOptions('/articles/me/all', 'GET', { page });
            const response = yield rq(options);
            return response;
        });
    }
    get hasApiKey() {
        return !!this._apiKey;
    }
    updateApiKey(apiKey) {
        this._apiKey = apiKey;
    }
    list() {
        return __awaiter(this, void 0, void 0, function* () {
            const articleList = [];
            let page = 1;
            let responseList;
            do {
                responseList = yield this._list(page);
                for (const response of responseList) {
                    articleList.push(response);
                }
                page++;
            } while (responseList.length > 0);
            return articleList;
        });
    }
    get(id) {
        return __awaiter(this, void 0, void 0, function* () {
            const options = this._buildRequestOptions('/articles/' + id, 'GET');
            const response = yield rq(options);
            return response;
        });
    }
    update(id, title, bodyMarkdown) {
        return __awaiter(this, void 0, void 0, function* () {
            const options = this._buildRequestOptions('/articles/' + id, 'PUT', undefined, { title, body_markdown: bodyMarkdown });
            const response = yield rq(options);
            return response;
        });
    }
    create(title, bodyMarkdown) {
        return __awaiter(this, void 0, void 0, function* () {
            const options = this._buildRequestOptions('/articles', 'POST', undefined, { title, body_markdown: bodyMarkdown });
            const response = yield rq(options);
            return response;
        });
    }
}
exports.DevAPI = DevAPI;

},{"request-promise":undefined}],4:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const rq = require("request-promise");
const fs = require("fs");
const path = require("path");
const DEFAULT_REPO_NAME = '_dev_community_post_images_';
const DEFAULT_REPO_DESCRIPTION = 'Auto created by DEV Community VS Code extension.';
class GitHubAPI {
    constructor(_personalToken) {
        this._personalToken = _personalToken;
        this._isRepoExist = {};
    }
    _buildRequestOptions(path, method, parameters, body) {
        let uri = `https://api.github.com${path}`;
        if (parameters) {
            let query = [];
            for (const parameterKey of Object.keys(parameters)) {
                query.push(`${parameterKey}=${parameters[parameterKey]}`);
            }
            uri += `?${query.join('&')}`;
        }
        const options = {
            uri,
            headers: {
                'User-Agent': 'vscode-devto;https://marketplace.visualstudio.com/items?itemName=sneezry.vscode-devto',
                'Authorization': `token ${this._personalToken}`,
            },
            method,
            json: true,
        };
        if (body) {
            options.body = body;
        }
        return options;
    }
    get hasToken() {
        return !!this._personalToken;
    }
    updatePersonalToken(personalToken) {
        this._personalToken = personalToken;
    }
    _getUserInfo() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._userInfo) {
                return this._userInfo;
            }
            const options = this._buildRequestOptions('/user', 'GET');
            const response = yield rq(options);
            this._userInfo = response;
            return response;
        });
    }
    _createRepo(repoName, repoDescription) {
        return __awaiter(this, void 0, void 0, function* () {
            const options = this._buildRequestOptions('/user/repos', 'POST', undefined, {
                name: repoName,
                description: repoDescription,
                has_issues: false,
                has_wiki: false,
                auto_init: true,
            });
            const response = yield rq(options);
            return response;
        });
    }
    _getRepo(repoName) {
        return __awaiter(this, void 0, void 0, function* () {
            const userInfo = yield this._getUserInfo();
            const options = this._buildRequestOptions(`/repos/${userInfo.login}/${repoName}`, 'GET');
            const response = yield rq(options);
            return response;
        });
    }
    _ensureRepo(repoName, repoDescription) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._isRepoExist[repoName]) {
                return;
            }
            try {
                yield this._getRepo(repoName);
            }
            catch (error) {
                yield this._createRepo(repoName, repoDescription);
            }
            this._isRepoExist[repoName] = true;
        });
    }
    _readFileAsBase64(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            return new Promise((resolve, reject) => {
                fs.readFile(uri.fsPath, { encoding: 'base64' }, (error, data) => {
                    if (error) {
                        return reject(error);
                    }
                    resolve(data);
                });
            });
        });
    }
    upload(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this._ensureRepo(DEFAULT_REPO_NAME, DEFAULT_REPO_DESCRIPTION);
            const userInfo = yield this._getUserInfo();
            const imageFileName = path.basename(uri.fsPath).replace(/\.([^\.]*?)$/, `.${Date.now().toString(36)}.$1`);
            const imageFileContent = yield this._readFileAsBase64(uri);
            const options = this._buildRequestOptions(`/repos/${userInfo.login}/${DEFAULT_REPO_NAME}/contents/${imageFileName}`, 'PUT', undefined, {
                message: `Upload ${imageFileName}`,
                content: imageFileContent,
            });
            const response = yield rq(options);
            return response;
        });
    }
}
exports.GitHubAPI = GitHubAPI;

},{"fs":undefined,"path":undefined,"request-promise":undefined}],5:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs = require("fs");
const rq = require("request-promise");
const CLIENT_ID = '7ad656873cab190';
class ImgurAPI {
    static _readFileAsBase64(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            return new Promise((resolve, reject) => {
                fs.readFile(uri.fsPath, { encoding: 'base64' }, (error, data) => {
                    if (error) {
                        return reject(error);
                    }
                    resolve(data);
                });
            });
        });
    }
    static upload(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            const imageFileContent = yield ImgurAPI._readFileAsBase64(uri);
            const options = {
                uri: 'https://api.imgur.com/3/upload',
                headers: {
                    'User-Agent': 'vscode-devto;https://marketplace.visualstudio.com/items?itemName=sneezry.vscode-devto',
                    'Authorization': `Client-ID ${CLIENT_ID}`,
                },
                method: 'POST',
                json: true,
                formData: {
                    image: imageFileContent,
                    type: 'base64',
                },
            };
            const response = yield rq(options);
            return response;
        });
    }
}
exports.ImgurAPI = ImgurAPI;

},{"fs":undefined,"request-promise":undefined}],6:[function(require,module,exports){
(function (Buffer){(function (){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const MetaParser_1 = require("./MetaParser");
const ResourceUriBuilder_1 = require("../content/ResourceUriBuilder");
const emptyArray = new Uint8Array(0);
class DevArticleVirtualFSProvider {
    constructor(api) {
        this.api = api;
        this._onDidChangeFile = new vscode.EventEmitter();
        this._articleList = [];
        this._articleListCached = false;
    }
    initialize() {
        return __awaiter(this, void 0, void 0, function* () {
            this._articleListCached = true;
            try {
                this._articleList = yield this.api.list();
            }
            catch (ignore) { }
        });
    }
    get onDidChangeFile() {
        return this._onDidChangeFile.event;
    }
    watch() {
        return {
            dispose: () => {
                // nothing to dispose
            }
        };
    }
    clearCache() {
        this._articleList = [];
        this._articleListCached = false;
    }
    readDirectory(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            if (/^[\\\/]$/.test(uri.path)) {
                if (!this._articleListCached) {
                    this._articleListCached = true;
                    try {
                        this._articleList = yield this.api.list();
                    }
                    catch (ignore) { }
                }
                return this._articleList.map((article) => {
                    return [encodeURIComponent(article.title) + '-0' + article.id + '.md', vscode.FileType.File];
                });
            }
            return [];
        });
    }
    // no need to support dir
    createDirectory(uri) { }
    readFile(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.api.hasApiKey) {
                return emptyArray;
            }
            const idMatched = uri.path.match(/0([\-]?[1-9]\d*)\.md$/);
            const id = idMatched ? Number(idMatched[1]) : 0;
            if (id < 0) {
                const buffer = Buffer.from(`---
title: 
published: false
description: 
tags: 
---

`, 'utf8');
                return new Uint8Array(buffer);
            }
            const article = this._articleList.find((item) => {
                return item.id === id;
            });
            if (!article || !article.body_markdown) {
                return emptyArray;
            }
            const buffer = uri.query === 'raw' ?
                Buffer.from(JSON.stringify(article), 'utf8') :
                Buffer.from(article.body_markdown, 'utf8');
            return new Uint8Array(buffer);
        });
    }
    delete(uri, options) {
        return __awaiter(this, void 0, void 0, function* () {
            const idMatched = uri.path.match(/0([\-]?[1-9]\d*)\.md$/);
            const id = idMatched ? Number(idMatched[1]) : 0;
            const article = this._articleList.find((article) => {
                return article.id === id;
            });
            if (article) {
                article.reserveTitle = undefined;
            }
            ;
        });
    }
    writeFile(uri, content, options) {
        return __awaiter(this, void 0, void 0, function* () {
            const markdown = content.toString();
            const title = MetaParser_1.titleParser(markdown);
            const published = MetaParser_1.publishStateParser(markdown);
            const idMatched = uri.path.match(/0([\-]?[1-9]\d*)\.md$/);
            const id = idMatched ? Number(idMatched[1]) : 0;
            const titleMatched = uri.path.match(/^[\\\/]?(.*?)\-0[\-]?[1-9]\d*\.md/);
            const oldTitle = decodeURIComponent(titleMatched ? titleMatched[1] : '');
            if (title) {
                if (id < 0) {
                    const article = {
                        id,
                        title,
                        body_markdown: markdown,
                        published: published,
                    };
                    this._articleList.unshift(article);
                }
                yield vscode.window.withProgress({
                    title: 'Saving ' + title + '-0' + id + '\'.md',
                    location: vscode.ProgressLocation.Notification,
                }, () => __awaiter(this, void 0, void 0, function* () {
                    try {
                        let newArticle;
                        if (id < 0) {
                            newArticle = yield this.api.create(title, markdown);
                        }
                        else {
                            newArticle = yield this.api.update(id, title, markdown);
                        }
                        // published property is missing in single update request response
                        if (newArticle.published === undefined) {
                            newArticle.published = published;
                        }
                        const newPostIndex = this._articleList.findIndex((article) => {
                            return article.id === id;
                        });
                        const newUri = ResourceUriBuilder_1.resourceUriBuilder({
                            title: newArticle.title,
                            id: newArticle.id,
                        });
                        newArticle.title = oldTitle;
                        newArticle.reserveTitle = oldTitle;
                        this._articleList[newPostIndex] = newArticle;
                        setTimeout(() => {
                            vscode.workspace.fs.rename(uri, newUri);
                        }, 0);
                    }
                    catch (error) {
                        console.error(error);
                        vscode.window.showWarningMessage('Failed to save \'' + title + '-0' + id + '\'.md. See console for details.');
                    }
                }));
            }
            else {
                vscode.window.showWarningMessage('😱 Heads up: title can\'t be blank.');
            }
        });
    }
    rename(oldUri, newUri, options) {
        return __awaiter(this, void 0, void 0, function* () {
            const idMatched = newUri.path.match(/0([\-]?[1-9]\d*)\.md$/);
            const id = idMatched ? Number(idMatched[1]) : 0;
            const titleMatched = newUri.path.match(/^[\\\/]?(.*?)\-0[\-]?[1-9]\d*\.md/);
            const title = decodeURIComponent(titleMatched ? titleMatched[1] : '');
            const article = this._articleList.find((article) => {
                return article.id === id;
            });
            if (article) {
                article.title = title;
            }
        });
    }
    stat(uri) {
        return __awaiter(this, void 0, void 0, function* () {
            if (/^[\\\/]$/.test(uri.path)) {
                return {
                    type: vscode.FileType.Directory,
                    ctime: 0,
                    mtime: 0,
                    size: 0,
                };
            }
            const idMatched = uri.path.match(/0([\-]?[1-9]\d*)\.md$/);
            const id = idMatched ? Number(idMatched[1]) : 0;
            const titleMatched = uri.path.match(/^[\\\/]?(.*?)\-0[\-]?[1-9]\d*\.md/);
            const title = decodeURIComponent(titleMatched ? titleMatched[1] : '');
            const article = this._articleList.find((article) => {
                return article.id === id;
            });
            if (id > 0 && (!article || article.title !== title && article.reserveTitle !== title)) {
                throw vscode.FileSystemError.FileNotFound();
            }
            return {
                type: vscode.FileType.File,
                ctime: 0,
                mtime: 0,
                size: 0,
            };
        });
    }
}
exports.DevArticleVirtualFSProvider = DevArticleVirtualFSProvider;

}).call(this)}).call(this,require("buffer").Buffer)
},{"../content/ResourceUriBuilder":9,"./MetaParser":8,"buffer":undefined,"vscode":undefined}],7:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const MetaParser_1 = require("./MetaParser");
const ResourceUriBuilder_1 = require("./ResourceUriBuilder");
class Edit {
    static showMarkdown(fileName) {
        return __awaiter(this, void 0, void 0, function* () {
            const uri = ResourceUriBuilder_1.resourceUriBuilder({ resourcePath: fileName });
            const doc = yield vscode.workspace.openTextDocument(uri);
            yield vscode.window.showTextDocument(doc, { preview: true });
        });
    }
    static createNewArticle() {
        return __awaiter(this, void 0, void 0, function* () {
            const uri = ResourceUriBuilder_1.resourceUriBuilder({
                title: 'Untitled',
                id: -Date.now(),
            });
            const doc = yield vscode.workspace.openTextDocument(uri);
            yield vscode.window.showTextDocument(doc, { preview: true });
        });
    }
    static getPublishedMarkdown(article) {
        let markdown = article.body_markdown;
        if (!markdown) {
            return;
        }
        const published = MetaParser_1.publishStateParser(markdown);
        if (published) {
            return;
        }
        const yaml = markdown.match(/^\s*\-{3}\n([\s\S]*?)\n\-{3}/);
        if (!yaml) {
            return;
        }
        const publishedState = yaml[1].match(/^\s*published:\s*(.*?)\s*$/m);
        if (!publishedState) {
            markdown = markdown.replace(/^\s*\-{3}\n([\s\S]*?)\n\-{3}/, '---\n$1\npublished: true\n---');
        }
        else {
            markdown = markdown.replace(/^\s*published:\s*(.*?)\s*$/m, 'published: true');
        }
        return markdown;
    }
    static publish(article) {
        return __awaiter(this, void 0, void 0, function* () {
            const markdown = Edit.getPublishedMarkdown(article);
            if (markdown) {
                const title = MetaParser_1.titleParser(markdown);
                const id = article.id;
                if (!title || !id) {
                    return;
                }
                const uri = ResourceUriBuilder_1.resourceUriBuilder({ title, id });
                const doc = yield vscode.workspace.openTextDocument(uri);
                const docText = doc.getText();
                const startPosition = new vscode.Position(0, 0);
                const endPosition = doc.positionAt(docText.length);
                const edit = new vscode.WorkspaceEdit();
                const range = new vscode.Range(startPosition, endPosition);
                edit.replace(uri, range, markdown);
                yield vscode.workspace.applyEdit(edit);
                yield doc.save();
            }
        });
    }
}
exports.Edit = Edit;

},{"./MetaParser":8,"./ResourceUriBuilder":9,"vscode":undefined}],8:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function titleParser(markdown) {
    const yaml = markdown.match(/^\s*\-{3}\n([\s\S]*?)\n\-{3}/);
    if (!yaml) {
        return null;
    }
    const title = yaml[1].match(/^[ \t]*title:[ \t]*(.*?)[ \t]*$/m);
    if (!title) {
        return null;
    }
    return decodeURIComponent(title[1]);
}
exports.titleParser = titleParser;
function publishStateParser(markdown) {
    const yaml = markdown.match(/^\s*\-{3}\n([\s\S]*?)\n\-{3}/);
    if (!yaml) {
        return false;
    }
    const published = yaml[1].match(/^[ \t]*published:[ \t]*(.*?)[ \t]*$/m);
    if (!published) {
        return false;
    }
    return published[1] === 'true';
}
exports.publishStateParser = publishStateParser;

},{}],9:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
function resourceUriBuilder(options) {
    const baseUri = 'devto://article/';
    let uriString;
    if (options && !options.resourcePath && options.title && options.id) {
        options.resourcePath = encodeURIComponent(options.title + '-0' + options.id) + '.md';
    }
    if (options && options.resourcePath) {
        // see https://github.com/microsoft/vscode/issues/45515#issuecomment-509178608
        uriString = baseUri + options.resourcePath.replace(/%2f/ig, '%252f');
        if (options.raw) {
            uriString += '?raw';
        }
    }
    else {
        uriString = baseUri;
    }
    return vscode.Uri.parse(uriString);
}
exports.resourceUriBuilder = resourceUriBuilder;

},{"vscode":undefined}],10:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const ApiKeyManager_1 = require("./ApiKeyManager");
const DevApi_1 = require("./api/DevApi");
const Edit_1 = require("./content/Edit");
const ResourceUriBuilder_1 = require("./content/ResourceUriBuilder");
const DevArticleVirtualFSProvider_1 = require("./content/DevArticleVirtualFSProvider");
const DevTreeDataProvider_1 = require("./view/DevTreeDataProvider");
const ImageUploadManager_1 = require("./ImageUploadManager");
const util_1 = require("util");
function getArticleByFileName(fileName) {
    return __awaiter(this, void 0, void 0, function* () {
        const uri = ResourceUriBuilder_1.resourceUriBuilder({
            resourcePath: fileName,
            raw: true,
        });
        const decoder = new util_1.TextDecoder();
        const articleRaw = decoder.decode(yield vscode.workspace.fs.readFile(uri));
        const article = JSON.parse(articleRaw);
        return article;
    });
}
function activate(context) {
    return __awaiter(this, void 0, void 0, function* () {
        const api = new DevApi_1.DevAPI();
        const apiKeyManager = new ApiKeyManager_1.DevApiKeyManager(context, api);
        const apiKey = yield apiKeyManager.getApiKey();
        if (apiKey) {
            api.updateApiKey(apiKey);
        }
        const treeDataProvider = new DevTreeDataProvider_1.DevTreeDataProvider(api);
        const devArticleVirtualFSProvider = new DevArticleVirtualFSProvider_1.DevArticleVirtualFSProvider(api);
        yield devArticleVirtualFSProvider.initialize();
        const uploadImageButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
        uploadImageButton.command = 'devto.uploadImage';
        uploadImageButton.text = '$(file-media) Upload images';
        uploadImageButton.tooltip = 'DEV Community: upload images to GitHub';
        const imageUploadManager = new ImageUploadManager_1.ImageUploadManager(context);
        context.subscriptions.push(vscode.workspace.registerFileSystemProvider('devto', devArticleVirtualFSProvider, { isCaseSensitive: true, isReadonly: false }), vscode.commands.registerCommand('devto.signin', () => __awaiter(this, void 0, void 0, function* () {
            yield apiKeyManager.updateApiKeyCommand(() => {
                devArticleVirtualFSProvider.clearCache();
                treeDataProvider.refresh();
            });
        })), vscode.commands.registerCommand('devto.uploadImage', () => __awaiter(this, void 0, void 0, function* () {
            yield imageUploadManager.uploadImage();
        })), vscode.commands.registerCommand('devto.updateGitHubPersonalToken', () => __awaiter(this, void 0, void 0, function* () {
            yield imageUploadManager.updateGitHubPersonalToken();
            vscode.window.showInformationMessage('Your GitHub personal access token has been updated.');
        })), vscode.commands.registerCommand('devto.removeGitHubPersonalToken', () => __awaiter(this, void 0, void 0, function* () {
            yield imageUploadManager.removeGitHubPersonalToken();
            vscode.window.showInformationMessage('Your GitHub personal access token has been removed.');
        })), vscode.commands.registerCommand('devto.view', (fileName) => __awaiter(this, void 0, void 0, function* () {
            const uri = ResourceUriBuilder_1.resourceUriBuilder({
                resourcePath: fileName,
                raw: true,
            });
            const decoder = new util_1.TextDecoder();
            const articleRaw = decoder.decode(yield vscode.workspace.fs.readFile(uri));
            const article = JSON.parse(articleRaw);
            if (article.url) {
                yield vscode.commands.executeCommand('vscode.open', vscode.Uri.parse(article.url));
            }
        })), vscode.commands.registerCommand('devto.editOnline', (fileName) => __awaiter(this, void 0, void 0, function* () {
            const article = yield getArticleByFileName(fileName);
            if (article.url) {
                yield vscode.commands.executeCommand('vscode.open', vscode.Uri.parse(article.url + '/edit'));
            }
        })), vscode.commands.registerCommand('devto.publish', (fileName) => __awaiter(this, void 0, void 0, function* () {
            const article = yield getArticleByFileName(fileName);
            yield vscode.window.withProgress({
                title: `Publishing ${article.title}`,
                location: vscode.ProgressLocation.Notification,
            }, () => __awaiter(this, void 0, void 0, function* () {
                yield Edit_1.Edit.publish(article);
                treeDataProvider.refresh();
            }));
        })), vscode.commands.registerCommand('devto.delete', (fileName) => __awaiter(this, void 0, void 0, function* () {
            const article = yield getArticleByFileName(fileName);
            if (article.url) {
                yield vscode.commands.executeCommand('vscode.open', vscode.Uri.parse(article.url + '/delete_confirm'));
            }
        })), vscode.commands.registerCommand('devto.key', () => __awaiter(this, void 0, void 0, function* () {
            yield vscode.commands.executeCommand('vscode.open', vscode.Uri.parse('https://dev.to/settings/account'));
        })), vscode.commands.registerCommand('devto.refresh', () => {
            if (!api.hasApiKey) {
                return;
            }
            devArticleVirtualFSProvider.clearCache();
            treeDataProvider.refresh();
        }), vscode.commands.registerCommand('devto.signout', () => __awaiter(this, void 0, void 0, function* () {
            yield apiKeyManager.removeApiKeyCommand(treeDataProvider.refresh.bind(treeDataProvider));
        })), vscode.commands.registerCommand('devto.create', Edit_1.Edit.createNewArticle), vscode.commands.registerCommand('devto.edit', Edit_1.Edit.showMarkdown), vscode.window.createTreeView('devto', {
            treeDataProvider,
        }), vscode.workspace.onDidSaveTextDocument((document) => __awaiter(this, void 0, void 0, function* () {
            if (document.uri.scheme === 'devto') {
                treeDataProvider.refresh();
            }
        })), vscode.window.onDidChangeActiveTextEditor((editor) => {
            if (editor && editor.document.uri.scheme === 'devto') {
                uploadImageButton.show();
            }
            else {
                uploadImageButton.hide();
            }
        }), uploadImageButton);
    });
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;

},{"./ApiKeyManager":1,"./ImageUploadManager":2,"./api/DevApi":3,"./content/DevArticleVirtualFSProvider":6,"./content/Edit":7,"./content/ResourceUriBuilder":9,"./view/DevTreeDataProvider":11,"util":undefined,"vscode":undefined}],11:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const util_1 = require("util");
const vscode = require("vscode");
const ResourceUriBuilder_1 = require("../content/ResourceUriBuilder");
class DevTreeDataProvider {
    constructor(_api) {
        this._api = _api;
        this.onDidChangeTreeDataEvent = new vscode.EventEmitter();
        this.onDidChangeTreeData = this.onDidChangeTreeDataEvent.event;
    }
    refresh() {
        this.onDidChangeTreeDataEvent.fire(null);
    }
    getChildren() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._api.hasApiKey) {
                const uri = ResourceUriBuilder_1.resourceUriBuilder();
                const fileList = yield vscode.workspace.fs.readDirectory(uri);
                return fileList.map((item) => {
                    return item[0];
                });
            }
            else {
                return ['Sign in', 'Create API key'];
            }
        });
    }
    getTreeItem(fileName) {
        return __awaiter(this, void 0, void 0, function* () {
            let command;
            if (fileName === 'Sign in') {
                return {
                    label: fileName,
                    tooltip: fileName,
                    id: fileName,
                    command: {
                        title: 'Sign in',
                        command: 'devto.signin',
                    },
                };
            }
            else if (fileName === 'Create API key') {
                return {
                    label: fileName,
                    tooltip: fileName,
                    id: fileName,
                    command: {
                        title: 'Create API key',
                        command: 'devto.key',
                    },
                };
            }
            else {
                command = {
                    title: 'Edit',
                    command: 'devto.edit',
                    arguments: [fileName],
                };
            }
            const uri = ResourceUriBuilder_1.resourceUriBuilder({
                resourcePath: fileName,
                raw: true,
            });
            const decoder = new util_1.TextDecoder();
            const articleRaw = decoder.decode(yield vscode.workspace.fs.readFile(uri));
            const article = JSON.parse(articleRaw);
            const commentCount = article.comments_count || 0;
            const positiveReactionsCount = article.positive_reactions_count || 0;
            const commentMeta = commentCount + (commentCount !== 1 ? ' comments' : ' comment');
            const positiveReactionsMeta = positiveReactionsCount + (positiveReactionsCount !== 1 ? ' reactions' : ' reaction');
            const treeItem = {
                label: article.title,
                tooltip: article.title + ' ・ ' + commentMeta + ' ・ ' + positiveReactionsMeta,
                id: `dev-${article.id}`,
                iconPath: vscode.ThemeIcon.File,
                resourceUri: ResourceUriBuilder_1.resourceUriBuilder({ resourcePath: fileName }),
                command,
            };
            if (article.id && article.id > 0 && !article.published) {
                treeItem.label = '[Draft] ' + treeItem.label;
                // hack for draft icon
                treeItem.resourceUri = ResourceUriBuilder_1.resourceUriBuilder({ resourcePath: 'readme.md' }),
                    treeItem.tooltip += ' ・ Draft';
                treeItem.contextValue = 'unpublished';
            }
            return treeItem;
        });
    }
}
exports.DevTreeDataProvider = DevTreeDataProvider;

},{"../content/ResourceUriBuilder":9,"util":undefined,"vscode":undefined}]},{},[10]);
