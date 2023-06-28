import CloudFlare

def main(args):
    token = args.get("token")
    zone = args.get('zone')
    record = args.get('record')
    ipv4 = args.get('ipv4')
    ipv6 = args.get('ipv6')
    cf = CloudFlare.CloudFlare(token=token)

    if not token:
        return {"statusCode": 500, 'body': 'Missing token URL parameter.'}
    if not zone:
        return {"statusCode": 500, 'body': 'Missing zone URL parameter.'}
    if not record:
        return {"statusCode": 500, 'body': 'Missing record URL parameter.'}
    if not ipv4 and not ipv6:
        return {"statusCode": 500, 'body': 'Missing ipv4 or ipv6 URL parameter.'}

    try:
        zones = cf.zones.get(params={'name': zone})

        if not zones:
            return {"statusCode": 500, 'body': 'Zone {} does not exist.'.format(zone)}

        a_record = cf.zones.dns_records.get(zones[0]['id'], params={
                                            'name': '{}.{}'.format(record, zone), 'match': 'all', 'type': 'A'})
        aaaa_record = cf.zones.dns_records.get(zones[0]['id'], params={
                                               'name': '{}.{}'.format(record, zone), 'match': 'all', 'type': 'AAAA'})

        if ipv4 is not None and not a_record:
            return {"statusCode": 500, 'body': 'A record for {}.{} does not exist.'.format(record, zone)}

        if ipv6 is not None and not aaaa_record:
            return {"statusCode": 500, 'body': 'AAAA record for {}.{} does not exist.'.format(record, zone)}

        if ipv4 is not None and a_record[0]['content'] != ipv4:
            cf.zones.dns_records.put(zones[0]['id'], a_record[0]['id'], data={
                                     'name': a_record[0]['name'], 'type': 'A', 'content': ipv4, 'proxied': a_record[0]['proxied'], 'ttl': a_record[0]['ttl']})

        if ipv6 is not None and aaaa_record[0]['content'] != ipv6:
            cf.zones.dns_records.put(zones[0]['id'], aaaa_record[0]['id'], data={
                                     'name': aaaa_record[0]['name'], 'type': 'AAAA', 'content': ipv6, 'proxied': aaaa_record[0]['proxied'], 'ttl': aaaa_record[0]['ttl']})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        return {"statusCode": 500, 'body': 'Cloudflare error: ' + str(e)}

    return {'statusCode': 200, 'headers': { 'Content-Type': 'application/json' }, 'body': 'Update successful.', 'ip': ipv4 }
