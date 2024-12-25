(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
const vscode = require('vscode');
const jw = require('./service/mapi-service');
const views = require('./views');

// Constants
const JW_ROOT = `https://cdn.jwplayer.com`;
const JW_SINGLELINE_URI = `players`;
const JW_CLOUDHOSTED_URI = `libraries`;
const JW_MANIFEST_URI = `manifests`;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    let savedKey;
    let savedSecret;
    let promptForCredentials;

    const configure =  () => {
        savedKey = context.globalState.get('jwApiKey');
        savedSecret = context.globalState.get('jwApiSecret');
        promptForCredentials = () => {
            vscode.window.showInputBox({
                prompt: 'Enter the API key for the property you would like to configure',
                placeHolder: 'API key',
                ignoreFocusOut: true,
            }).then((key) => {
                // Prompt for secret and then add both to global state
                vscode.window.showInputBox({
                    prompt: `Enter the API secret for ${key}`,
                    placeholder: 'API secret',
                    ignoreFocusOut: true,
                }).then((secret) => {
                    if (!key || !secret) {
                        return vscode.window.showErrorMessage('JW Link: Failed to save credentials');
                    }
                    if (validateCredentialsLength(key, secret)) {
                        context.globalState.update('jwApiKey', key);
                        context.globalState.update('jwApiSecret', secret);
                        savedKey = key;
                        savedSecret = secret;
                        vscode.commands.executeCommand('jwLink.refresh');
                    } else {
                        vscode.window.showErrorMessage('JW Link: Credentials are invalid', 'Try Again').then(option => {
                            if (option === 'Try Again') {
                                vscode.commands.executeCommand('jwLink.configure');
                            }
                        });
                    }
                });
            }).catch((err) => {
                vscode.window.showErrorMessage('JW Link: Failed to save credentials', err);
            });
        };

        if (savedKey && savedSecret) {
            vscode.window.showInformationMessage(
                'JW Link: Your API credentials are already saved.', // message
                'Update Credentials' // button
            ).then(option => {
                if (option === 'Update Credentials') {
                    promptForCredentials();
                }
            });
        } else {
            promptForCredentials();
        }
    };

    const refresh = () => {
        if (!savedKey && !savedSecret) {
            promptForCredentials();
        }
        jw.getPlayers(context);
        jw.getContent(context);
    };

    const generateSingleLineEmbed = () => {
        views.displayPlayers(context).then(playerChoice => {
            views.displayContent(context).then(contentChoice => {
                insertText(`${JW_ROOT}/${JW_SINGLELINE_URI}/${contentChoice.mediaid}-${playerChoice.pid}.js`);
            });
        });
    };

    const generateCloudHostedPlayerURI = () => {
        views.displayPlayers(context).then(playerChoice => {
            insertText(`${JW_ROOT}/${JW_CLOUDHOSTED_URI}/${playerChoice.pid}.js`);
        })
    };

    const generateHlsManifestURI = () => {
        views.displayContent(context).then(contentChoice => {
            insertText(`${JW_ROOT}/${JW_MANIFEST_URI}/${contentChoice.mediaid}.m3u8`);
        });
    };

    const insertText = (text) => {
        const editor = vscode.window.activeTextEditor;

        if (editor) {
            editor.edit(edit => {
                edit.insert(editor.selection.active, text);
            })
        }
    };

    const validateCredentialsLength = (key, secret) => {
        return key.length === 8 && secret.length === 24;
    };

    vscode.commands.registerCommand('jwLink.configure', configure);
    vscode.commands.registerCommand('jwLink.refresh', refresh);
    vscode.commands.registerCommand('jwLink.singleLine', generateSingleLineEmbed);
    vscode.commands.registerCommand('jwLink.player', generateCloudHostedPlayerURI);
    vscode.commands.registerCommand('jwLink.content', generateHlsManifestURI);
    vscode.commands.registerCommand('jwLink.moreOptions', () => { views.moreOptions(context) });
}

exports.activate = activate;

function deactivate() {}

module.exports = {
    activate,
    deactivate
}

},{"./service/mapi-service":2,"./views":3,"vscode":undefined}],2:[function(require,module,exports){
const vscode = require('vscode');
const axios = require('axios');
const jwApi = require('jwplayer-api');
const fs = require('fs');
const path = require('path');

const JW_PLAYERS_ENDPOINT = `v1/players/list`;

let jwApiInstance;

const getPlayers = (extensionContext) => {
    const credentials = {
        key: extensionContext.globalState.get('jwApiKey'),
        secret: extensionContext.globalState.get('jwApiSecret')
    };

    const playersPath = path.join(extensionContext.globalStoragePath, 'players.json');

    // Create folder for extension data
    fs.mkdir(extensionContext.globalStoragePath, err => {
        // Only throw errors other than if folder already exists
        if (err & err.code !== 'EEXIST') {
            vscode.window.showErrorMessage('JW Link: Failed to create extension folder');
        }
    });

    if (credentials.key && credentials.secret) {
        jwApiInstance = new jwApi({
            key: credentials.key,
            secret: credentials.secret
        });

        return axios({
            method: 'get',
            url: jwApiInstance.generateUrl(JW_PLAYERS_ENDPOINT)
        }).then(res => {
            fs.writeFile(playersPath, JSON.stringify(res.data.players), err => {
                if (err) {
                    return vscode.window.showErrorMessage('JW Link: Failed to save players');
                }
                vscode.window.showInformationMessage('JW Link: Saved players');
            })
        });
    } else {
        // If no credentials found, prompt user with option to add credentials
        vscode.window.showErrorMessage('JW Link: Credentials not found', 'Add Credentials').then(option => {
            if (option === 'Add Credentials') {
                vscode.commands.executeCommand('jwLink.configure');
            }
        });
    }
};

const getContent = (extensionContext) => {
    const credentials = {
        key: extensionContext.globalState.get('jwApiKey'),
        secret: extensionContext.globalState.get('jwApiSecret')
    };

    const contentPath = path.join(extensionContext.globalStoragePath, 'content.json');

    // Create folder for extension data
    fs.mkdir(extensionContext.globalStoragePath, err => {
        // Only throw errors other than if folder already exists
        if (err & err.code !== 'EEXIST') {
            vscode.window.showErrorMessage('JW Link: Failed to create extension folder');
        }
    });

    if (credentials.key && credentials.secret) {
        if (!jwApiInstance) {
            jwApiInstance = new jwApi({
                key: credentials.key,
                secret: credentials.secret
            });
        }

        jwApiInstance.videosList().then(res => {
            fs.writeFile(contentPath, JSON.stringify(res.videos), err => {
                if (err) {
                    return vscode.window.showErrorMessage('JW Link: Failed to save list of content');
                }
                vscode.window.showInformationMessage('JW Link: Saved list of content');
            });
        });
    } else {
        // If no credentials found, prompt user with option to add credentials
        vscode.window.showErrorMessage('JW Link: Credentials not found', 'Add Credentials').then(option => {
            if (option === 'Add Credentials') {
                vscode.commands.executeCommand('jwLink.configure');
            }
        });
    }
};

module.exports = {
    getPlayers,
    getContent
};

},{"axios":undefined,"fs":undefined,"jwplayer-api":undefined,"path":undefined,"vscode":undefined}],3:[function(require,module,exports){
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

function displayPlayers(extensionContext) {
    const playersPath = path.join(extensionContext.globalStoragePath, 'players.json');
    const players = require(playersPath);
    const playersArray = [];
    players.forEach(player => {
        playersArray.push({
            label: player.name,
            description: `Version: ${player.version} | ID: ${player.key}`,
            pid: player.key
        })
    });
    return vscode.window.showQuickPick(playersArray);
}

function displayContent(extensionContext) {
    const contentPath = path.join(extensionContext.globalStoragePath, 'content.json');
    const content = require(contentPath);
    const contentArray = [];
    content.forEach(video => {
        contentArray.push({
            label: video.title,
            description: `ID: ${video.key}`,
            mediaid: video.key
        });
    });
    return vscode.window.showQuickPick(contentArray);
}

function moreOptions(extensionContext) {
    vscode.window.showQuickPick(['Remove API Credentials']).then(option => {
        if (option === 'Remove API Credentials') {
            extensionContext.globalState.update('jwApiKey', null);
            extensionContext.globalState.update('jwApiSecret', null);
            const playersPath = path.join(extensionContext.globalStoragePath, 'players.json');
            const contentPath = path.join(extensionContext.globalStoragePath, 'content.json');
            try {
                fs.unlinkSync(playersPath);
                fs.unlinkSync(contentPath);
            } catch (error) {
                vscode.window.showErrorMessage('JW Link: Could not delete saved list of players/content.');
            }

        }
        vscode.window.showInformationMessage(`JW Link: Credentials removed. Run 'Update Credentials' command to add new credentials.`);
    })
}

module.exports = {
    displayPlayers,
    displayContent,
    moreOptions
};

},{"fs":undefined,"path":undefined,"vscode":undefined}]},{},[1]);
