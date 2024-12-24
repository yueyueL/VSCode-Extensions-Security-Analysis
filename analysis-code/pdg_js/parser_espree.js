module.exports = {
    js2ast: js2ast,
};


var fs = require("fs");
var espree = require("espree");
var es = require("escodegen");
var process = require("process");

/**
 * Extraction of the AST of an input JS file using Esprima.
 *
 * @param js
 * @param json_path
 * @returns {*}
 */

function js2ast(js, json_path) {
    var text = fs.readFileSync(js).toString('utf-8');
    try {
        var ast = espree.parse(text, {
        range: true,
        loc: true,
        tokens: true,
        tolerant: true,
        comment: true,
        ecmaVersion : 14
        });
    } catch(e) {
        console.error(js, e);
        process.exit(1);
    }
    // Attaching comments is a separate step for Escodegen
    ast = es.attachComments(ast, ast.comments, ast.tokens);

    fs.writeFile(json_path, JSON.stringify(ast), function (err) {
        if (err) {
            console.error(err);
        }
    });

    return ast;
}
  
js2ast(process.argv[2], process.argv[3]);