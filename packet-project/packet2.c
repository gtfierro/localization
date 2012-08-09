#include <stdio.h>
#include <stdlib.h>
#include <pcap.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netinet/if_ether.h>

int main(int argc, char **argv)
{
  int i;
  char *dev;
  char errbuf[PCAP_ERRBUF_SIZE];
  pcap_t* descr;
  const u_char *packet;
  struct pcap_pkthdr hdr;
  struct ether_header *eptr;

  u_char *ptr;

  /* get a device */
  dev = "wlan0";

  printf("DEV: %s\n", dev);

  /* 
   * open device for sniffing:
   * pcap_t *pcap_open_live(char *device, int snaplen, int prmisc, int to_ms, char #ebuf)
   */
  
  descr = pcap_open_live(dev, BUFSIZ, 0, 0, errbuf);

  if (descr == NULL)
  {
    printf("pcap_open_live(): %s\n", errbuf);
    exit(1);
  }

  /* get packet from descr
   * u_char *pcap_next(pcap_t *p, struct pcap_pkthdr *h)
   */

  printf("Waiting for packet...\n");

  packet = pcap_next(descr, &hdr);

  printf("Got packet!\n");

  if (packet == NULL)
  {
    printf("Didn't grab packet\n");
    exit(1);
  }

  /* struct pcap_pkthdr {
   * struct timeval ts; time stamp
   * bpf_u_int32 caplen; length of portion present
   * bpf_u_int32; length of this packet
   * }
   */

  printf("Got packet of length %d\n", hdr.len);
  printf("Received at %s\n", ctime((const time_t*)&hdr.ts.tv_sec));
  printf("Ethernet address length is %d\n", ETHER_HDR_LEN);

  /* parse the ethernet header */
  eptr = (struct ether_header *) packet;

  /* check what type of packet we got */
  if (ntohs (eptr-> ether_type) == ETHERTYPE_IP)
  {
    printf("Ethernet type hex:%x dec%d is an IP packet\n",
        ntohs(eptr->ether_type),
        ntohs(eptr->ether_type));
  } else if (ntohs(eptr->ether_type) == ETHERTYPE_ARP)
  {
    printf("Ethernet type hex:%x dec:%d is an ARP packet\n",
        ntohs(eptr->ether_type),
        ntohs(eptr->ether_type));
  } else {
    printf("Ethernet type %x not IP", ntohs(eptr->ether_type));
    exit(1);
  }

  ptr = eptr->ether_dhost;
  i = ETHER_ADDR_LEN;
  printf("Destination Address: ");
  do {
    printf("%s%x", (i == ETHER_ADDR_LEN) ? " " : ":", *ptr++);
  } while (--i>0);
  printf("\n");

  ptr = eptr->ether_shost;
  i = ETHER_ADDR_LEN;
  printf("Source Address: ");
  do {
    printf("%s%x", (i == ETHER_ADDR_LEN) ? " " : ":", *ptr++);
  } while (--i>0);
  printf("\n");

  return 0;
}





