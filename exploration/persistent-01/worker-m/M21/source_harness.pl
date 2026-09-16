use strict; use warnings; use Digest::SHA qw(sha1); use JSON::PP; use FindBin; use lib "$FindBin::Bin/sources/Convert-ASCII-Armour-1.4/lib"; use Convert::ASCII::Armour;
sub readfile { my $p=shift; open my $f,'<',$p or die $!; local $/; return <$f>; }
# Upstream routines are extracted verbatim; only their unavailable dependency bindings are supplied.
sub extract { my($s,$name)=@_; $s =~ /(^sub \Q$name\E\s*\{.*?)(?=^sub |^1;)/ms or die "Missing $name"; return $1; }
sub PARI { return $_[0] } # used only for small MGF counters 0..500 and base256, never RSA integers
sub debug {}
sub makerandom_octet { return pack('C*',0..19) } # reproducible synthetic OAEP seed
sub error { my($self,$msg)=@_; $self->{error}=$msg; return undef }
my $df=readfile("$FindBin::Bin/sources/Crypt-RSA-1.99/lib/Crypt/RSA/DataFormat.pm");
my $oa=readfile("$FindBin::Bin/sources/Crypt-RSA-1.99/lib/Crypt/RSA/ES/OAEP.pm");
for my $name(qw(i2osp octet_xor mgf1)){eval extract($df,$name); die $@ if $@}
for my $name(qw(encode decode hash mgf)){eval extract($oa,$name); die $@ if $@}
my $self=bless {hlen=>20},'main';
my $request=decode_json(readfile($ARGV[0]));my @rows;
for my $v(@{$request->{vectors}}){my $msg=pack('H*',$v->{message_hex});my $em=$self->encode($msg,'',$v->{emlen});defined $em or die 'encode failed';my $back=$self->decode($em,'');defined($back) && $back eq $msg or die 'roundtrip failed';push @rows,{message_hex=>unpack('H*',$back),em_hex=>unpack('H*',$em),emlen=>$v->{emlen}};}
my @historic;for my $em(@{$request->{historical_em_hex}}){my $plain=$self->decode(pack('H*',$em),'');push @historic,{ok=>defined($plain)?JSON::PP::true:JSON::PP::false,message_hex=>defined($plain)?unpack('H*',$plain):'',error=>$self->{error}};}
my $armour=Convert::ASCII::Armour->new();my $parsed=$armour->unarmour($request->{armour}) or die $armour->errstr();my $rearmour=$armour->armour(Object=>'RSA ENCRYPTED MESSAGE',Headers=>$parsed->{Headers},Content=>$parsed->{Content},Compress=>1);my $back=$armour->unarmour($rearmour) or die $armour->errstr();$back->{Content}{Cyphertext} eq $parsed->{Content}{Cyphertext} or die 'container roundtrip';
print encode_json({vectors=>\@rows,historical=>\@historic,container_cipher_hex=>unpack('H*',$parsed->{Content}{Cyphertext}),container_headers=>$parsed->{Headers},container_roundtrip=>JSON::PP::true,perl=>$^V."",digest_sha=>$Digest::SHA::VERSION,dependency_limits=>'small integer PARI identity, Digest::SHA SHA1, fixed synthetic random seed; RSA arithmetic independently Python only'});
