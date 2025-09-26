#!/bin/bash

# Common headers
AUTH="Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlVzRUN0ZmczWWVVYTkxeV9LLXk1WSJ9...." # shorten for readability
HEADERS=(
  -H "accept: application/json, text/plain, */*"
  -H "accept-language: fr-FR,fr;q=0.9,en;q=0.8,en-US;q=0.7"
  -H "authorization: $AUTH"
  -H "conf: all_trends"
  -H "origin: https://market-trends.heuritech.com"
  -H "referer: https://market-trends.heuritech.com/"
  -H "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

# List of URLs
URLS=(
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=fabrics:female:casual_everyday&verticals=fabrics:female:performance_sportswear&verticals=fabrics:female:nightlife_formalwear&verticals=fabrics:female:outerwear_protective_fabrics&verticals=fabrics:female:delicate_transparent_fabrics"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=colors:female:neutral_tones&verticals=colors:female:warm_tones&verticals=colors:female:cool_tones&verticals=colors:female:metallic&verticals=colors:female:pastel&verticals=colors:female:light_pastel&verticals=colors:female:fluo"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=prints:female:plain&verticals=prints:female:geometric&verticals=prints:female:organic&verticals=prints:female:graphic&verticals=prints:female:heritage&verticals=prints:female:thematic"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=dress:female:shapes&verticals=dress:female:lengths&verticals=dress:female:sleevelengths&verticals=dress:female:sleevetypes&verticals=dress:female:collars&verticals=dress:female:necklines&verticals=dress:female:styles"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=skirt:female:shapes&verticals=skirt:female:lengths&verticals=skirt:female:asymmetricalattribute&verticals=skirt:female:pleatedattribute&verticals=skirt:female:ruffledattribute&verticals=skirt:female:wrappedattribute&verticals=skirt:female:splittedattribute&verticals=skirt:female:subwaistattribute&verticals=skirt:female:waistline&verticals=skirt:female:buttonline&verticals=skirt:female:closure&verticals=skirt:female:pocketattribute&verticals=skirt:female:otherattribute"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=shorts:female:shapes&verticals=shorts:female:lengths&verticals=shorts:female:fits&verticals=shorts:female:pockets&verticals=shorts:female:embellishments&verticals=shorts:female:waistline&verticals=shorts:female:waistattributes&verticals=shorts:female:waistaccessories&verticals=shorts:female:hemfinish"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=pants:female:shapes&verticals=pants:female:lengths&verticals=pants:female:fits&verticals=pants:female:pockets&verticals=pants:female:stitchingdetails&verticals=pants:female:waistline&verticals=pants:female:waistattributes&verticals=pants:female:waistaccessories&verticals=pants:female:embellishments&verticals=pants:female:waistopeningtype&verticals=pants:female:waistopeningsplacement&verticals=pants:female:hemfinish&verticals=pants:female:rolleduphems"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=top:female:shapes&verticals=top:female:lengths&verticals=top:female:fits&verticals=top:female:sleevelengths&verticals=top:female:sleevetypes&verticals=top:female:necklines&verticals=top:female:collars&verticals=top:female:closure&verticals=top:female:shoulders"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=outerwear:female:shapes&verticals=outerwear:female:lengths&verticals=outerwear:female:fits&verticals=outerwear:female:sleevelengths&verticals=outerwear:female:pocketstype&verticals=outerwear:female:hoodtype&verticals=outerwear:female:collars&verticals=outerwear:female:pockets"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=boots:female:shapes&verticals=boots:female:toeshape&verticals=boots:female:heeltype&verticals=boots:female:heelheight&verticals=boots:female:shaftheight&verticals=boots:female:platform&verticals=boots:female:closure&verticals=boots:female:soleeffect"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=dress_shoes:female:shapes&verticals=dress_shoes:female:toeshape&verticals=dress_shoes:female:heeltype&verticals=dress_shoes:female:heelheight&verticals=dress_shoes:female:backtype&verticals=dress_shoes:female:closure&verticals=dress_shoes:female:platform"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=sandals:female:shapes&verticals=sandals:female:toeshape&verticals=sandals:female:heelheight&verticals=sandals:female:heeltype&verticals=sandals:female:backtype&verticals=sandals:female:closure&verticals=sandals:female:platform"
"https://markettrends-api.heuritech.com/product_architectures/verticals?geo_zone=us&verticals=sneakers:female:shapes&verticals=sneakers:female:closure&verticals=sneakers:female:sneakerheight&verticals=sneakers:female:soleheight&verticals=sneakers:female:soleeffect&verticals=sneakers:female:platform"
)

# Loop through URLs
i=1
for url in "${URLS[@]}"; do
  echo "Fetching $url"
  curl -s "$url" "${HEADERS[@]}" > "output_$i.json"
  ((i++))
done

echo "✅ Done. Results saved to output_1.json, output_2.json, ..."

