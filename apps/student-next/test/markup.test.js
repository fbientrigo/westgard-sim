// test/markup.test.js
import test from "node:test";
import assert from "node:assert/strict";
import { renderCardMarkup } from "../src/markup.js";

test("markup: renders supported semantic token", () => {
  const html = renderCardMarkup("[[rule:1-2s]]");
  assert.match(html, /semantic-rule/);
  assert.match(html, /Regla/);
  assert.match(html, /1-2s/);
});

test("markup: renders bold", () => {
  assert.equal(renderCardMarkup("**importante**"), "<strong>importante</strong>");
});

test("markup: renders italic", () => {
  assert.equal(renderCardMarkup("*énfasis*"), "<em>énfasis</em>");
});

test("markup: renders code", () => {
  assert.equal(renderCardMarkup("`1_2s`"), "<code>1_2s</code>");
});

test("markup: leaves an unbalanced marker literal", () => {
  assert.equal(renderCardMarkup("**sin cierre"), "**sin cierre");
});

test("markup: escapes unsafe HTML before supported markup", () => {
  const html = renderCardMarkup("<script>alert(1)</script> y **seguro**");
  assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(html, /<strong>seguro<\/strong>/);
  assert.doesNotMatch(html, /<script>/);
});

test("markup: unsupported semantic kind remains literal escaped content", () => {
  assert.equal(renderCardMarkup("[[unknown:texto]]"), "[[unknown:texto]]");
});
