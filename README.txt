
$ curl 'https://post.ca.gov/Peace-Officer-Certification-Actions' > all.txt
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  264k  100  264k    0     0   584k      0 --:--:-- --:--:-- --:--:--  583k
$
$ ls -l
-rw-rw-r-- 1 ray ray 271212 Jan 21 11:16 all.txt

The html for one officer, as returned by bs4, is:

<tr>
<td>Davis </td>
<td>Gregory Brian</td>
<td>
<p>Surrendered</p>
</td>
<td>
<p>08/23/2024</p>
</td>
<td></td>
<td>Los Angeles County SD (last employed 10/24/2023)</td>
<td>
<p>Voluntary Surrender</p>
</td>
</tr>

