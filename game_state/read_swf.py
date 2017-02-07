# -*- coding: utf-8 -*-
import zlib

class RECT:
    def __init__(self,xmin,xmax,ymin,ymax): #not in usual order
        self.xmin=xmin
        self.xmax=xmax
        self.ymin=ymin
        self.ymax=ymax
class Reader:
    def __init__(self):
        self.pos = 0
        self.subpos = 0
    def reset_subpos(self):
        self.pos += self.subpos/8 + (1 if self.subpos%8 else 0)
        self.subpos = 0
    def readUI(self,bit_length):
        self.reset_subpos()
        data = 0
        for i in xrange(0,bit_length,8):
            data = data + (ord(self.contents[self.pos]) << i)
            self.pos+=1
        return data
    def readU30(self):
        self.reset_subpos()
        data = 0
        for i in xrange(0,35,7):
            byte_read = ord(self.contents[self.pos])
            data = data + ((byte_read & 0x7f) << i)
            self.pos+=1
            if not (byte_read & 0x80):
                break
        return data
    def readUI8(self):
        return self.readUI(8)
    def readUI16(self):
        return self.readUI(16)
    def readUI24(self):
        return self.readUI(24)
    def readUI32(self):
        return self.readUI(32)
    def read_bytes(self,count):
        self.reset_subpos()
        data = self.contents[self.pos:(self.pos+count)]
        self.pos+=count
        return data
    def read_bit(self):
        data = (ord(self.contents[self.pos])>>(7-self.subpos))&1
        self.subpos += 1
        self.pos += self.subpos / 8
        self.subpos %= 8
        return data
    def read_bits(self,count):
        data = 0
        for i in xrange(count):
            data=(data<<1) + self.read_bit()
        return data
    def read_string(self):
        self.reset_subpos()
        count=self.contents[self.pos:].find('\x00')
        data=self.contents[self.pos:(self.pos+count)]
        self.pos+=count+1
        return data
    def skip(self,bytes_count):
        if bytes_count<0:
            return
        self.reset_subpos()
        self.pos+=bytes_count
    
class SWF(Reader):
    def __init__(self,data):
        Reader.__init__(self)
        self.contents = data #fp.read()
        if self.contents[0] == 'C':
            self.original = self.contents
            self.contents = self.contents[:8]+zlib.decompress (self.contents[8:])
    def read_RECT(self):
        n_bits = self.read_bits(5)
        coords=[]
        for i in xrange(4):
            coords.append(self.read_bits(n_bits))
        xmin,xmax,ymin,ymax = coords
        return RECT(xmin,xmax,ymin,ymax)
    def read_header(self):
        self.signature = self.read_bytes(3)
        self.version = self.readUI8()
        self.file_length = self.readUI32()
        self.frame_size = self.read_RECT()
        self.frame_rate = self.readUI16() / 256.0
        self.frame_count = self.readUI16()
        self.header_end_1 = self.pos
    def read_record_header(self):
        tag_code_and_length = self.readUI16()
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3f
        if tag_length == 0x3f:
            tag_length = self.readUI32()
        return tag_type, tag_length
    def read_frames(self):
        self.frames=[]
        tag_type = None
        while (tag_type != 0):
            tag_type, tag_length = self.read_record_header()
            self.frames.append((tag_type, tag_length, self.pos))
            self.pos+=tag_length
    def read_DoABC(self):
        self.DoABC_flags = self.readUI32()
        self.DoABC_name = self.read_string()
        #self.pos_ABC = self_pos
    def find_ABC(self):
        for (tag_type, tag_length, tag_pos) in self.frames:
            if tag_type == 82:#DoABC
                break
        self.pos=tag_pos
        self.read_DoABC()
        return self.contents[self.pos:(tag_pos+tag_length)]

class ABC(Reader):
    def __init__(self,contents):
        Reader.__init__(self)
        self.contents=contents
        '''
        u16 minor_version
        u16 major_version
        cpool_info constant_pool
        u30 method_count
        method_info method[method_count]
        u30 metadata_count
        metadata_info metadata[metadata_count]
        u30 class_count
        instance_info instance[class_count]
        class_info class[class_count]
        u30 script_count
        script_info script[script_count]
        u30 method_body_count
        method_body_info method_body[method_body_count]
        '''
        self.minor_version = self.readUI16()
        self.major_version = self.readUI16()
        self.constant_pool = self.read_cpool_info()
        self.method_count = self.readU30()
        self.methods=[]
        for i in xrange(self.method_count):
            self.methods.append(self.read_method())
        self.metadata_count, self.metadata = self.read_metadata()
        self.class_count = self.readU30()
        self.instances=[]
        for i in xrange(self.class_count):
            self.instances.append(self.read_instance())
        self.classes=[]
        for i in xrange(self.class_count):
            self.classes.append(self.read_class())
        self.script_count=self.readU30()
        self.scripts=[]
        for i in xrange(self.script_count):
            self.scripts.append(self.read_class())
        self.method_body_count=self.readU30()
        self.method_body_info=[self.read_method_body() for i in xrange(self.method_body_count)]
            
        
    def read_cpool_info(self):
        '''
        cpool_info
        {
        u30 int_count
        s32 integer[int_count]
        u30 uint_count
        u32 uinteger[uint_count]
        u30 double_count
        d64 double[double_count]
        u30 string_count
        string_info string[string_count]
        u30 namespace_count
        namespace_info namespace[namespace_count]
        u30 ns_set_count
        ns_set_info ns_set[ns_set_count]
        u30 multiname_count
        multiname_info multiname[multiname_count]
        }'''
        self.int_count = self.readU30()
        self.skip(self.int_count*4)
        self.uint_count = self.readU30()
        self.skip(self.uint_count*4)
        self.dounle_count = self.readU30()
        self.skip(self.dounle_count*8)
        self.string_count = self.readU30()
        self.strings=['null']
        for i in xrange(self.string_count-1):
            self.strings.append('"'+self.read_string_info()+'"')
        self.namespace_count = self.readU30()
        self.namespaces=['*']
        for i in xrange(self.namespace_count-1):
            kind=self.readUI8()
            name=self.readU30()
            self.namespaces.append(Namespace(self.strings,kind,name))
        self.ns_set_count = self.readU30()
        if self.ns_set_count:
            self.ns_sets=[[]]
            for i in xrange(self.ns_set_count-1):
                count = self.readU30()
                namespaces = []
                for j in xrange(count):
                    namespaces.append(self.namespaces[self.readU30()])
                self.ns_sets.append(namespaces)
        else:
            self.ns_sets=[]
        self.multiname_count = self.readU30()
        self.multinames=['null']
        for i in xrange(self.multiname_count-1):
            kind = self.readUI8()
            multiname_kind,v=self.multiname[kind]
            self.multinames.append('%s(%s)'%(multiname_kind,
                                        ','.join(str(j) for j in v())))
        
    def read_string_info(self):
        size = self.readU30()
        return self.read_bytes(size)
    
    @property
    def multiname(self):
        return {0x07:('QName',lambda:[self.ns,self.name]),
                0x0D:('QNameA',lambda:[self.ns,self.name]),
                0x0F:('RTQName',lambda:[self.name]),
                0x10:('RTQNameA',lambda:[self.name]),
                0x11:('RTQNameL',lambda:[]),
                0x12:('RTQNameLA',lambda:[]),
                0x09:('Multiname',lambda:[self.name,self.ns_set]),
                0x0E:('MultinameA',lambda:[self.name,self.ns_set]),
                0x1B:('MultinameL',lambda:[self.ns_set]),
                0x1C:('MultinameLA',lambda:[self.ns_set])}
    @property
    def name(self):
        return self.strings[self.readU30()]
    @property
    def ns(self):
        return self.namespaces[self.readU30()]
    @property
    def ns_set(self):
        return '[%s]'%(','.join(str(i) for i in self.ns_sets[self.readU30()]))

    def read_method(self):
        '''
        method_info
        {
        u30 param_count
        u30 return_type
        u30 param_type[param_count]
        u30 name
        u8 flags
        option_info options
        param_info param_names
        }
        '''
        data={}
        data['param_count']=self.readU30()
        data['return_type']=self.readU30() #multiname
        data['param_type']=[]
        for i in xrange(data['param_count']):
            data['param_type'].append(self.readU30()) #multiname
        data['name']=self.readU30() #string
        data['flags']=self.readUI8()
        flags={'NEED_ARGUMENTS': 0x01,
               'NEED_ACTIVATION': 0x02,
               'NEED_REST': 0x04,
               'HAS_OPTIONAL': 0x08,
               'SET_DXNS': 0x40,
               'HAS_PARAM_NAMES': 0x80}
        if data['flags'] & flags['HAS_OPTIONAL']:
            data['option_info']=self.read_method_option_info() ##
        if data['flags'] & flags['HAS_PARAM_NAMES']:
            data['param_name']=[]
            for i in xrange(data['param_count']):
                data['param_name'].append(self.readU30()) #string
        return data

    def read_metadata(self):
        res_metadata=[]
        res_metadata_count = self.readU30()
        for i in xrange(res_metadata_count):
            metadata={}
            metadata['name']=self.readU30()
            metadata['item_count']=self.readU30()
            metadata['items']=[(self.readU30(),self.readU30()) for j in xrange(metadata['item_count'])]
            res_metadata.append(metadata)
        return res_metadata_count, res_metadata

    def read_instance(self):
        '''
        instance_info
        {
        u30 name
        u30 super_name
        u8 flags
        u30 protectedNs
        u30 intrf_count
        u30 interface[intrf_count]
        u30 iinit
        u30 trait_count
        traits_info trait[trait_count]
        }'''
        data={}
        data['name']=self.readU30() #multiname
        data['super_name']=self.readU30() #multiname
        data['flags']=self.readUI8()
        flags={'ClassSealed': 0x01,
               'ClassFinal': 0x02,
               'ClassInterface': 0x04,
               'ClassProtectedNs': 0x08,
               }
        if data['flags'] & flags['ClassProtectedNs']:
            data['protectedNs']=self.readU30() #namespace
        data['intrf_count']=self.readU30()
        data['interface']=[self.readU30() for i in xrange(data['intrf_count'])] #multiname
        self.read_class(data)
        return data

    def read_trait(self):
        '''
        traits_info
        {
        u30 name
        u8 kind
        u8 data[]
        u30 metadata_count
        u30 metadata[metadata_count]
        }'''
        data={}
        data['name']=self.readU30() #multiname
        data['kind']=self.readUI8()
        trait_type,trait_attrs = data['kind']&0x0f, data['kind']>>4
        trait_types={0:('Trait_Slot',lambda:[self.readU30(),self.readU30(),self.readU30(),self.readUI8()]),
                     1:('Trait_Method',lambda:[self.readU30(),self.readU30()]),
                     2:('Trait_Getter',lambda:[self.readU30(),self.readU30()]),
                     3:('Trait_Setter',lambda:[self.readU30(),self.readU30()]),
                     4:('Trait_Class',lambda:[self.readU30(),self.readU30()]),
                     5:('Trait_Function',lambda:[self.readU30(),self.readU30()]),
                     6:('Trait_Const',lambda:[self.readU30(),self.readU30(),self.readU30(),self.readUI8()])}
        data['data']=trait_types[trait_type][1]()
        attrs={'ATTR_Final': 0x1,
               'ATTR_Override': 0x2,
               'ATTR_Metadata': 0x4}
        if trait_attrs & attrs['ATTR_Metadata']:
            data['metadata_count'],data['metadata']=self.read_metadata()
        return data

    def read_class(self,data={}):
        '''
        class_info
        {
        u30 cinit
        u30 trait_count
        traits_info traits[trait_count]
        }'''
        data['init']=self.readU30() #method
        self.read_traits(data)
        return data

    def read_traits(self,data={}):
        data['trait_count']=self.readU30()
        data['trait']=[self.read_trait() for i in xrange(data['trait_count'])]
        return data

    def read_method_body(self):
        '''
        method_body_info
        {
        u30 method
        u30 max_stack
        u30 local_count
        u30 init_scope_depth
        u30 max_scope_depth
        u30 code_length
        u8 code[code_length]
        u30 exception_count
        exception_info exception[exception_count]
        u30 trait_count
        traits_info trait[trait_count]
        }'''
        fields=['method',
                'max_stack',
                'local_count',
                'init_scope_depth',
                'max_scope_depth',
                'code_length']
        data={field:self.readU30() for field in fields}
        data['code']=self.read_bytes(data['code_length'])
        data['exception_count']=self.readU30()
        data['exception']=[self.read_exception_info() for i in xrange(data['exception_count'])]
        self.read_traits(data)
        return data
        
    def read_exception_info(self):
        '''
        exception_info
        {
        u30 from
        u30 to
        u30 target
        u30 exc_type
        u30 var_name
        }'''
        fields=['from',
                'to',
                'target',
                'exc_type',
                'var_name']
        data={field:self.readU30() for field in fields}

class Namespace:
    def __init__(self,strings,kind,name):
        self.strings = strings
        self.kind = kind
        self.name = name
    @property
    def kinds(self):
        return {0x08:'Namespace',
                0x16:'PackageNamespace',
                0x17:'PackageInternalNs',
                0x18:'ProtectedNamespace',
                0x19:'ExplicitNamespace',
                0x1A:'StaticProtectedNs',
                0x05:'PrivateNs'}
#    @property
#    def name(self):
#        return self.kinds[self.kind]+'("'+self.strings[self.name]+'")'
    def __str__(self):
        return self.kinds[self.kind]+'('+self.strings[self.name]+')'

class Code_Reader(Reader):
    def __init__(self,code,strings,multinames):
        Reader.__init__(self)
        self.contents = code
        self.strings = strings
        self.multinames = multinames
        self.opcodes = {0xd1:('getlocal_1',[]),
                        0xd2:('getlocal_2',[]),
                        0xd6:('setlocal_2',[]),
                        0x85:('coerce_s',[]),
                        0x60:('getlex',['m']),
                        0x66:('getproperty',['m']),
                        0x2c:('pushstring',['s']),
                        0x42:('construct',['d']),
                        0x46:('callproperty',['m','d']),
                        0x24:('pushbyte',['u8']),
                        0xa0:('add',[]),
                        0xa3:('divide',[]),
                        0xa2:('multiply',[]),
                        0x48:('returnvalue',[]),
                        0x5d:('findpropstrict',['m'])
                        }
        self.args = {'m':lambda:self.multinames[self.readU30()],
                     'd':self.readU30,
                     's':lambda:self.strings[self.readU30()],
                     'u8':self.readUI8}
    def read(self):
        res=[]
        while self.pos < len(self.contents):
            opcode = self.readUI8()
            operation, args = self.opcodes[opcode]
            res.append(' '.join([operation]+[str(self.args[i]()) for i in args]))
        return res
    
class SWFParseError(Exception):
    pass
    
def swf2functions(data,postfix,selected_site):
    if selected_site == 'mr':
        url = 's.shadowlands.ru/zombiemr-res/'
    elif selected_site == 'ok':
        url = 's.shadowlands.ru/zombieok-res/'
    else:
        url = 's.shadowlands.ru/zombievk-res/'
    swf=SWF(data)
    swf.read_header()
    swf.read_frames()
    abc=ABC(swf.find_ABC())
    #print abc.strings
    #print abc.multinames
    #print abc.methods
    #print self.method_body_count
    code=abc.method_body_info[1]['code']
    code_reader=Code_Reader(code,abc.strings,abc.multinames)
    read_code=code_reader.read()
    #print read_code
    read_code_str='\n'.join(read_code)
    #print read_code_str
    functions=[(['getlocal_1', 'coerce_s', 'setlocal_2'],
                lambda(x):x),
               (['getlocal_2',
                 'getlex QName(PackageNamespace(""),"loaderInfo")',
                 'getproperty QName(PackageNamespace(""),"loaderURL")',
                 'getlex QName(PackageNamespace(""),"RegExp")',
                 'pushstring "^.+\\/"',
                 'construct 1',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"match") 1',
                 'pushbyte 0',
                 'getproperty MultinameL([PrivateNs(null),PackageNamespace(""),Namespace("http://adobe.com/AS3/2006/builtin"),PrivateNs(null),PackageInternalNs(""),ProtectedNamespace("SaltGenerator'+postfix+'"),StaticProtectedNs("SaltGenerator'+postfix+'"),StaticProtectedNs("flash.display:Sprite"),StaticProtectedNs("flash.display:DisplayObjectContainer"),StaticProtectedNs("flash.display:InteractiveObject"),StaticProtectedNs("flash.display:DisplayObject"),StaticProtectedNs("flash.events:EventDispatcher")])',
                 'getlex QName(PackageNamespace(""),"RegExp")',
                 'pushstring "^.*\\/\\/"',
                 'construct 1',
                 'pushstring ""',
                 'callproperty Multiname("replace",[PrivateNs(null),PackageNamespace(""),Namespace("http://adobe.com/AS3/2006/builtin"),PrivateNs(null),PackageInternalNs(""),ProtectedNamespace("SaltGenerator'+postfix+'"),StaticProtectedNs("SaltGenerator'+postfix+'"),StaticProtectedNs("flash.display:Sprite"),StaticProtectedNs("flash.display:DisplayObjectContainer"),StaticProtectedNs("flash.display:InteractiveObject"),StaticProtectedNs("flash.display:DisplayObject"),StaticProtectedNs("flash.events:EventDispatcher")]) 2',
                 'add', 'coerce_s', 'setlocal_2'],
                lambda(x):x+url),
               (['getlocal_2',
                 'getlex QName(PackageNamespace(""),"RegExp")',
                 'pushstring "0"',
                 'pushstring "gi"',
                 'construct 2',
                 'pushstring "1"',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"replace") 2',
                 'coerce_s','setlocal_2'],
                lambda(x):x.replace('0','1')),
               (['getlocal_2',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"toLowerCase") 0',
                 'coerce_s', 'setlocal_2'],
                lambda(x):x.lower()),
               (['getlocal_2',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"toUpperCase") 0',
                 'coerce_s', 'setlocal_2'],
                lambda(x):x.upper()),
               (['getlocal_2', 'coerce_s', 'setlocal_2'],
                lambda(x):x),
               (['getlocal_2',
                 'pushbyte 0',
                 'getlocal_2',
                 'getproperty QName(PackageNamespace(""),"length")',
                 'pushbyte 2',
                 'divide',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"substring") 2',
                 'coerce_s', 'setlocal_2'],
                lambda(x):x[:len(x)/2]),
               (['findpropstrict QName(PackageNamespace(""),"String")',
                 'getlocal_2',
                 'getproperty QName(PackageNamespace(""),"length")',
                 'pushbyte 13',
                 'multiply',
                 'callproperty QName(PackageNamespace(""),"String") 1',
                 'coerce_s', 'setlocal_2'],
                lambda(x):str(len(x)*13)),
               (['getlocal_2', 'getlocal_2', 'add', 'coerce_s', 'setlocal_2'],
                lambda(x):x+x),
               (['getlocal_2',
                 'pushstring ""',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"split") 1',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"reverse") 0',
                 'pushstring ""',
                 'callproperty QName(Namespace("http://adobe.com/AS3/2006/builtin"),"join") 1',
                 'coerce_s', 'setlocal_2'],
                lambda(x):''.join(reversed(list(x))))
               ]
    fns=[]
    fnums=[]
    while read_code_str != 'getlocal_2\nreturnvalue':
        for i,(strs,f) in enumerate(functions):
            start_str = '\n'.join(strs)
            if read_code_str.startswith(start_str):
                fns.append(f)
                fnums.append(i)
                read_code_str = read_code_str[len(start_str+'\n'):]
                break
        else:
            with open('salt'+postfix+'.swf','wb') as f:
                f.write(swf.original)
                #print fnums
            raise SWFParseError('Something\'s wrong, please send the swf to the author')
            break
    else:
        return fns[1:]
'''
(C) 2014 megabyte
'''
